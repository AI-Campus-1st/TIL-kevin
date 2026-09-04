import streamlit as st
import pandas as pd

st.title('데이터 표현')
st.write('### 표와 메트릭')

columns = st.columns(2)

with columns[0]:
    st.metric('온도', '25°C', '1.2°C')
with columns[1]:
    st.metric('습도', '60%', '-5%')

st.divider()

data = [
    ['사과', '포도', '배', '오렌지', '수박'],
    [1, 3, 5, 7, 9],
]
st.table(data)

st.divider()

st.toast('데이터 불러오기 성공', duration='short')

data = {
    '종류': ['사과', '포도', '배', '오렌지', '수박'],
    '재고': [1, 3, 5, 7, 9],
}
df = pd.DataFrame(data)
st.table(df)

st.divider()

st.dataframe(df)

data = {
    '이름': '홍길동',
    '나이': 30,
    '주소': {
        '도시': '서울',
        '구': '강남구'
    }
}

st.json(data)
