# app.py
import streamlit as st
from ui.book_search import run_search_books
from ui.page1 import run_1



def main():
    st.title("📚 아~~ 이 책 뭐였지?")
    st.markdown("""🔍 **기억나시는 대로 줄거리를 입력하면 그 내용과 비슷한 책을 찾아드립니다.**  
                네이버 제공 도서 정보를 기반으로 검색됩니다.  
                소설의 엔딩보다는 시작 부분을 입력하시는 것이 더 정확한 검색 결과를 얻는 데 도움이 됩니다.""")
    st.markdown("---")
    if 'page' not in st.session_state:
        st.session_state.page = 'book_search' 

    if st.session_state.page == 'book_search':
        st.empty()
        run_search_books()
    elif st.session_state.page == 'page1':
        st.empty()
        run_1()


if __name__ == "__main__":
    main()
