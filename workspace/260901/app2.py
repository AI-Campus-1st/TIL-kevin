import streamlit as st
import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [10, 11, 12, 13, 14],
    'category': ['A', 'B', 'A', 'B', 'A']
})

fig = px.scatter(df, x='x', y='y', color='category',
                 title='Plotly Streamlit 연동')

st.title('Plotly 연동 예제')
st.plotly_chart(fig)

# matplotlib, seaborn
# st.pyplot(fig)

st.markdown('<p style="color: green; font-weight: 700;">초록색</p> 기본 마크다운', 
            unsafe_allow_html=True)

st.write('<p style="text-align:center";>가운데정렬</p>', 
         unsafe_allow_html=True)
st.text('')
st.markdown('가운데 정렬', text_alignment='center')


st.markdown("""
|헤더1|헤더2|
|---|---|
|값1|값2|
|값3|값4|
""")