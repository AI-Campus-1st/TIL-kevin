import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from plotly.subplots import make_subplots

engine = create_engine('sqlite:///stocks.db')


def load_data():
    with engine.connect() as conn:
        query = "SELECT * FROM stocks ORDER BY timestamp DESC LIMIT 100"
        return pd.read_sql(query, conn)

data = load_data()

st_autorefresh(interval=1000)
st.title("Real-Time Stock Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    latest_price = data['price'].iloc[0]
    st.metric(label="Latest Price", value=f"${latest_price:.2f}")

with col2:
    latest_volume = data['volume'].iloc[0]
    st.metric(label="Latest Volume", value=f"{latest_volume}")

with col3:
    price_change = latest_price - data['price'].iloc[1]
    volume_change = latest_volume - data['volume'].iloc[1]
    st.metric(label="Price Change", value=f"${price_change:.2f}", delta=f"{price_change:.2f}")
    st.metric(label="Volume Change", value=f"{volume_change}", delta=f"{volume_change}")

# 서브플롯 생성
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    row_heights=[0.7, 0.3], vertical_spacing=0.1, subplot_titles=(["Stock Price & Volume", ""]))

# 라인 차트 (주식 가격)
fig.add_trace(go.Scatter(x=data['timestamp'], y=data['price'], mode='lines', name='Price', line=dict(color='blue')), row=1, col=1)

# 막대 차트 (거래량)
fig.add_trace(go.Bar(x=data['timestamp'], y=data['volume'], name='Volume', marker=dict(color='orange')), row=2, col=1)

# 레이아웃 설정
fig.update_layout(
    height=600,
    title='Stock Price and Volume',
    # xaxis=dict(title='Time'),
    yaxis=dict(title='Price'),
    yaxis2=dict(title='Volume'),
    showlegend=False
)

# 차트 표시
st.plotly_chart(fig)

# 데이터 테이블
with st.expander("View Raw Data"):
    st.write(data)
