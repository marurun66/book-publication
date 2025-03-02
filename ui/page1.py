import os
import time
import requests
import streamlit as st
import toml
import urllib


# 📌 secrets.toml에서 Naver API 키 가져오기
def get_naver_api_keys():
    config = toml.load('./.streamlit/secrets.toml')
    return config['NAVER_CLIENT_ID'], config['NAVER_CLIENT_SECRET']

# 📌 네이버 API를 사용하여 책 정보를 가져오는 함수
def get_book_info_from_naver(book_title):
    client_id, client_secret = get_naver_api_keys()
    url = "https://openapi.naver.com/v1/search/book.json"
    params = {
        'query': book_title,  # 검색할 책 제목
        'display': 1  # 결과를 1개만 보여줌
    }
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['items']:
            book = data['items'][0]
            return {
                'title': book['title'],
                'author': book['author'],
                'publisher': book['publisher'],
                'image': book['image'],
                'description': book['description']
            }
    return None


# 피드백 저장 함수
def save_feedback():
    feedback_text = st.session_state.get("feedback_text", "")  # 폼에서 입력된 피드백을 가져옴
    if not feedback_text:  # 피드백 내용이 없을 경우 경고
        st.warning("피드백을 입력해 주세요.")  # 피드백이 없을 경우 경고
        return  # 피드백이 없으면 저장하지 않음

    file_path = "book_feedback.txt"
    user_story = st.session_state["user_story"]
    # 의견을 파일에 저장
    with open(file_path, "a") as f:
        f.write(f"Story: {user_story}\n")
        f.write(f"Feedback: {feedback_text}\n")
        f.write("-" * 40 + "\n")  # 구분선 추가
    # 피드백 저장 상태를 True로 설정
    st.session_state["feedback_saved"] = True
    st.success("피드백이 저장되었습니다! 감사합니다.")
    st.session_state["book_index"] = 0  # 검색이 끝났으니 인덱스 초기화
    st.session_state["books_displayed"] = []  # 리스트 초기화
    st.session_state.page = "book_search"  # 페이지 전환



# 📌 UI 실행 함수
def run_1():

    if "book_index" not in st.session_state:
        st.session_state["book_index"] = 0  # 첫 번째 책부터 시작

    if "books_displayed" not in st.session_state:
        st.session_state["books_displayed"] = []  # 책 정보를 저장할 리스트 초기화

    if "books_not_found" not in st.session_state or len(st.session_state["books_not_found"]) == 0:
        st.error("🔍 검색할 책이 없습니다.")
        return

    # 현재 책 정보 가져오기
    book_index = st.session_state["book_index"]
    book = st.session_state["books_not_found"][book_index]

    # 네이버 API를 사용하여 책 정보 가져오기
    book_info = get_book_info_from_naver(book['title'])

    if book_info:
        # 책 정보 중복 추가 방지
        if book_info not in st.session_state["books_displayed"]:
            st.session_state["books_displayed"].append(book_info)

        # 저장된 책 목록 출력
        for idx, displayed_book in enumerate(st.session_state["books_displayed"]):
            col1, col2 = st.columns([4, 2])
            with col1:
                st.subheader(f"📚 이 책일까요? - 후보 {idx + 1}")  
                st.subheader(f"📖 **{displayed_book['title']}**")
                st.write(f"✍️ 작가: {displayed_book['author']}")
                st.write(f"📌 출판사: {displayed_book['publisher']}")

            with col2:
                st.image(displayed_book['image'], caption=displayed_book['title'], width=200)
            
            st.write(f"📜 책 설명:\n{displayed_book['description']}")
            st.write("---")
    else:
        st.write(f"❌ '{book['title']}'에 대한 정보를 찾을 수 없습니다.")

    # ✅ "이 책이 맞아요" 버튼
    if st.button("✅ 이 책이 맞아요", key=f"book_{book_index}_yes"):
        st.success(f"🎉 '{book['title']}' 책을 찾았습니다!")
        st.balloons()
        st.session_state["book_index"] = 0  # 검색이 끝났으니 인덱스 초기화
        st.session_state["books_displayed"] = []  # 리스트 초기화
        st.session_state.page = "book_search"  # 페이지 전환
        time.sleep(2)
        st.rerun()
    user_story = st.session_state["user_story"]+"라는 줄거리의 소설은"
    encoded_user_story = urllib.parse.quote(user_story)

    # 피드백 저장
    if st.button("❌ 이 책이 아니에요", key=f"book_{book_index}_no"):
        # 책 인덱스 증가
        if st.session_state["book_index"] < len(st.session_state["books_not_found"]) - 1:
            st.session_state["book_index"] += 1  # 다음 책으로 이동
        else:
            st.write("❌ 더 이상 후보가 없습니다. 구글에서 검색해볼까요?")
            st.markdown(f"[구글에서 줄거리를 검색](https://www.google.com/search?q={encoded_user_story})")

            # 피드백 텍스트 박스
            if "feedback_saved" not in st.session_state:
                st.session_state["feedback_saved"] = False  # 초기값 설정

            # 폼을 사용하여 피드백을 받음
            with st.form(key="feedback_form"):
                st.text_area("이 책이었을 것 같아요 (의견을 남겨주세요)", placeholder="책에 대한 의견을 남겨주세요...", key="feedback_text")
                st.form_submit_button("피드백 저장", on_click=save_feedback)  # on_click으로 함수 지정
                
