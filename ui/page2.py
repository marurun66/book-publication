import streamlit as st
@st.cache_data(ttl=3600)
def run_2():
    st.title("피드백을 남겨주세요")
    st.write("이 책 뭐더라? 서비스를 이용해 주셔서 감사합니다. 아래 피드백을 남겨주시면 더 나은 서비스로 발전하도록 노력하겠습니다.")
    st.write("📚 이 책 뭐더라? 팀")
    st.write("📧 이메일: dd")

    if st.button("🔙 뒤로 가기"):
        st.session_state.page = "book_search"
        st.rerun()