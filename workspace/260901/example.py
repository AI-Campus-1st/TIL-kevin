import streamlit as st

st.set_page_config(layout="wide")

st.title('Streamlit 레이아웃 설정 예제')
st.write('이 예제는 Streamlit의 다양한 레이아웃 기능을 보여줍니다.')

with st.sidebar:
    st.title('사이드바')
    # st.sidebar.write('## 사이드바')

    st.write('여기에 사이드바 내용을 추가할 수 있습니다.')
    v = st.slider('사이드바 슬라이더', 0, 100, 25)

    st.write(f'선택된 값: {v}')


cols = st.columns([0.3, 1.5, 0.5])

with cols[0]:
    st.write('## 컬럼 1')
    st.write('여기는 첫 번째 칼럼입니다.')
    st.button('컬럼 1 버튼')

with cols[1]:
    st.write('## 컬럼 2')
    st.write('여기는 두 번째 칼럼입니다.')
    st.button('컬럼 2 버튼')

with cols[2]:
    st.write('## 컬럼 3')

with st.expander('더보기'):
    st.write('여기에 추가 정보를 넣을 수 있습니다.')

    with st.container(width='content', horizontal_alignment='center'):
        st.markdown('![예시 이미지](https://placehold.co/150x150/EEE/33343C)')
        st.markdown('<span style="color: gray;">예시 이미지</span>', 
                    text_alignment='center', unsafe_allow_html=True)
