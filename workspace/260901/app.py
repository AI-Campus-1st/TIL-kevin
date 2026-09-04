import streamlit as st

if 'page' not in st.session_state:
    st.session_state['page'] = 0

if st.session_state['page'] == 0:

    # 1. 위에서부터 아래로 widget이 쌓인다.
    st.title('첫 번째 대시보드')
    st.write('### 대시보드 앱 개발 시작')

    st.write('새로 저장')

    st.write('always rerun하면 개발할때 유용함')

    with st.sidebar:
        st.title('메뉴')

    # 실행
    # streamlit run app.py (파일 경로)

    v = st.button('클릭')
    print('if문 밖', v)
    if v:
        print('if문 안', v)
        st.success('성공')

    vol = st.slider('볼륨', 0, 100, 25)
    print('볼륨 값:', vol)

    # (print가 다 실행된다.)
    # 2. 상호작용이 있은 뒤에 모든 코드가 다시 실행된다.

    # 3. 저장을 할때마다 rerun (auto rerun) 다시 실행 
    # (파일 변경할때마다)

    # 결론: streamlit은 사용자의 상호작용이 있은 뒤에, 
    # 전체 코드를 다시 실행한다.

    columns = st.columns(3)

    with columns[0]:
        v = st.text_input('이메일 주소')
        print('텍스트입력:', v)
    with columns[1]:
        v = st.number_input('나이', step=1)
        print('나이:', v)
    with columns[2]:
        v = st.text_area('자기소개', max_chars=300, height=36)
        print('자기소개:', v)

elif st.session_state['page'] == 1:
    st.title('About 페이지입니다.')

with st.sidebar:
    st.write('## 필터')

with st.expander('더보기'):
    st.write('## 짜잔 \n 더보기 내용입니다.')



with st.sidebar:
    if st.button('home'):
        st.session_state['page'] = 0
    if st.button('about'):
        st.session_state['page'] = 1


st.line_chart([3, 5, 7, 7, 8])


