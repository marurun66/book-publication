import streamlit as st
import faiss
import json
import requests
from sentence_transformers import SentenceTransformer
@st.cache_data(ttl=3600)
def load_faiss():
    return faiss.read_index("./modeling/book_faiss_cosine_index.bin")
@st.cache_data(ttl=3600)
def load_books():
    with open("./data/merged_books_filtered.json", "r", encoding="utf-8") as f:
        return json.load(f)

def search_naver_api(user_query):
    client_id = st.secrets["NAVER_CLIENT_ID"]
    client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    url = "https://openapi.naver.com/v1/search/book.json"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": user_query,
        "display": 5,
        "sort": "sim"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        st.warning(f"🚨 네이버 API 호출 실패: {response.status_code}")
        return []
@st.cache_data(ttl=3600)
def find_similar_books(user_story, top_k=5):
    faiss_index = load_faiss()
    books_data = load_books()
    book_titles = [book["title"] for book in books_data]
    book_summaries = [book["summary"] for book in books_data]

    embedding_model = SentenceTransformer("BM-K/KoSimCSE-roberta")
    user_embedding = embedding_model.encode([user_story], convert_to_numpy=True)
    faiss.normalize_L2(user_embedding)

    distances, indices = faiss_index.search(user_embedding, top_k)

    recommended_books = []
    for i in range(top_k):
        idx = indices[0][i]
        title = book_titles[idx]
        summary = book_summaries[idx]
        recommended_books.append({"title": title, "summary": summary})

    return recommended_books

def run_search_books():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        pass
    with col2:
        st.image("image/pose_souzou_woman.png",width=300)
    with col3:
        if st.button("👩🏻‍💻 개발과정 보러가기"):
            st.session_state.page = "page2"
            st.rerun()
    st.markdown("""
        <div style="position: relative; background-color: #fdfdfd; padding: 10px 25px 5px 65px; border-radius: 0px 10px; border: 1px solid #e5e5e5; box-shadow: 1px 2px 3px 1px rgba(0,0,0,.1);">
            <div style="position: absolute; top: -1px; left: 14px; width: 30px; height: 47px; background-color: #a7e7c4;">&nbsp;</div>
            <div style="position: absolute; top: 17px; left: 14px; width: 0; height: 0; border: 15px solid; border-color: transparent transparent #fdfdfd transparent;">&nbsp;</div>
            <h2 style="color: #333333; font-family: 'Georgia', Arial;">🔍 이 책 뭐더라??</h2>
            <p style="color: #555555; font-size: 16px; font-family: 'Arial', sans-serif;">
                스토리는 어렴풋이 생각 나는데...<br>
                책 제목이 기억나지 않으신다고요?<br>
                <strong>대략의 줄거리를 입력하면 그 내용과 비슷한 책을 찾아드립니다.</strong><br>
                <strong>네이버에서 제공되는 소설 데이터 중, 줄거리가 공개된 1,322권을 기반으로 검색</strong>되며,<br>
                소설의 엔딩보다는 <strong>시작 부분을 입력</strong>하시는 것이 더 정확한 검색 결과를 얻는 데 도움이 됩니다.
            </p>
            <p style="color: #777777; font-size: 14px; font-family: 'Arial', sans-serif; text-align: center;">
                📚 <span style="font-weight: bold;">책을 찾고 싶다면 스토리를 입력해보세요!</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")





    # 처음 상태 설정
    if "book_index" not in st.session_state:
        st.session_state["book_index"] = 0  # 첫 번째 책을 보여줍니다.
    if "books_not_found" not in st.session_state:
        st.session_state["books_not_found"] = []

    user_story = st.text_area("🔹 스토리를 입력하세요.", placeholder="한 고아소년이 마법사가 되는 소설")
    st.session_state['user_story'] = user_story
    if st.button("🔍 도서 찾기"):
        if not user_story.strip():
            st.warning("스토리를 입력해주세요.")
            return
        faiss_results = find_similar_books(user_story, top_k=5)

        if faiss_results:
            st.session_state["books_not_found"] = faiss_results  # 책 정보를 세션에 저장
            st.session_state["book_index"] = 0  # 첫 번째 책을 보여주기 위해 인덱스 초기화
            st.session_state["is_searched"] = True  # 검색이 완료되었음을 표시
            st.session_state.page = "page1"  # 첫 번째 책 페이지로 이동
        else:
            st.warning("검색된 책이 없습니다.")

