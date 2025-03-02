import streamlit as st
import faiss
import json
import requests
from sentence_transformers import SentenceTransformer

def load_faiss():
    return faiss.read_index("./modeling/book_faiss_cosine_index.bin")

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