import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택하세요!',['라따뚜이','오페라케이크','알리오올리오'])
if st.button('인사말 생성'):
  st.info(a+'님, 안녕하세요! 반갑습니다!')
st.warning(b+'를 좋아하시군요! 저도 좋아해요!')
st.error('반가워요!!')
st.balloons()
