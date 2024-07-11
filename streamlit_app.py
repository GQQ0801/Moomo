import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import altair as alt
import time
import random
import zipfile
import uuid
import requests
from auth_util import gen_sign_headers

# APP_ID、APP_KEY
APP_ID = '3031446984'
APP_KEY = 'RwRvYgFQmUPiEKvj'
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

def sync_vivogpt(messages,prompt):
    params = {
        'requestId': str(uuid.uuid4())
    }
    print('requestId:', params['requestId'])

    data = {
        'messages': messages,
        'model': 'vivo-BlueLM-TB',
        'sessionId': str(uuid.uuid4()),
        'systemPrompt':'你的名字叫Moomo情绪探测助手，当回复问题时需要回复你的名字时，必须回复Moomo情绪探测助手，此外回复和你的名字相关的问题时，也需要给出和你的名字对应的合理回复。',
        'extra': {
            'temperature': 0.9
        }
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    start_time = time.time()
    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=data, headers=headers, params=params)
    
    print(messages)
    
    if response.status_code == 200:
        res_obj = response.json()
        #print(f'response:{res_obj}')
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']
            print(f'回答:\n{content}')
            return content
    else:
        print(response.status_code, response.text)
    end_time = time.time()
    timecost = end_time - start_time 
    print('请求耗时: %.2f秒' % timecost)

# Page title
st.set_page_config(page_title='Moomo', page_icon='🌈')
st.title('Moomo')

with st.expander('应用介绍'):
  st.markdown('**Moomo——基于蓝心大模型的文本分析工具**')
  st.info('以对话形式， 引导用户进行表达，通过用户自然表达，帮助用户觉察情绪，更好地进行心理疗愈。“Moomo” 旨在利用最前沿的人工智能技术，打造一个全天候、个性化的心理健康伙伴，填补市场对高效、深度情绪管理工具的需求空白。')

  st.markdown('**使用方式**')
  st.warning('通过输入框与AI聊天助手进行对话。')

# 初始化session
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "我是你的情绪探测助手Moomo,有什么话都可以和我说哦~"})
# 渲染历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 

# 接收用户输入
if prompt := st.chat_input("请在此输入"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response=sync_vivogpt(st.session_state.messages,prompt)
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response:
            full_response += chunk
            time.sleep(0.1)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
  
import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data


@st.cache_data
def get_data():
    source = data.stocks()
    source = source[source.date.gt("2004-01-01")]
    return source


stock_data = get_data()

hover = alt.selection_single(
    fields=["date"],
    nearest=True,
    on="mouseover",
    empty="none",
)

lines = (
    alt.Chart(stock_data, title="Evolution of stock prices")
    .mark_line()
    .encode(
        x="date",
        y="price",
        color="symbol",
    )
)

points = lines.transform_filter(hover).mark_circle(size=65)

tooltips = (
    alt.Chart(stock_data)
    .mark_rule()
    .encode(
        x="yearmonthdate(date)",
        y="price",
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[
            alt.Tooltip("date", title="Date"),
            alt.Tooltip("price", title="Price (USD)"),
        ],
    )
    .add_selection(hover)
)

data_layer = lines + points + tooltips

ANNOTATIONS = [
    ("Sep 01, 2007", 450, "🙂", "Something's going well for GOOG & AAPL."),
    ("Nov 01, 2008", 220, "🙂", "The market is recovering."),
    ("Dec 01, 2007", 750, "😱", "Something's going wrong for GOOG & AAPL."),
    ("Dec 01, 2009", 680, "😱", "A hiccup for GOOG."),
]
annotations_df = pd.DataFrame(
    ANNOTATIONS, columns=["date", "price", "marker", "description"]
)
annotations_df.date = pd.to_datetime(annotations_df.date)

annotation_layer = (
    alt.Chart(annotations_df)
    .mark_text(size=20, dx=-10, dy=0, align="left")
    .encode(x="date:T", y=alt.Y("price:Q"), text="marker", tooltip="description")
)

combined_chart = data_layer + annotation_layer
st.altair_chart(combined_chart, use_container_width=True)
