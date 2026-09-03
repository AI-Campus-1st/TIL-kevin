import streamlit as st
import pandas as pd
import time

start_time=time.time()
@st.cache_data
def load_data():
    df=pd.read_csv('2019-Oct-small.csv',encoding='cp949')
    return df

data=load_data()
st.dataframe(data.head())
elapsed=time.time()-start_time

st.write(f'소요시간: {elapsed}')
st.write('캐시 데이터 적용')