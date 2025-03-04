import json
import streamlit as st

def load_books():
    with open("./data/merged_books_filtered.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_books_count():
    try:
        books_data = load_books() 
        return len(books_data)
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError:
        return 0

def run_2():

    book_count = get_books_count()

    st.title("📚 이 책 뭐더라? 어플 개발 프로세스")
    st.markdown("""
        이 어플은 사용자가 기억나는데로 입력한 책 줄거리와 유사한 책을 찾아주는 웹 어플리케이션입니다.
                """
                )

    col1, col2,col3 = st.columns([1, 1,1])
    with col1:
        st.header("📌 개발 툴")
        st.markdown(
            """
        ✔ 데이터 수집, 전처리, 모델 학습: Jupyter Notebook  
        ✔ 코드 통합: Visual Studio Code (코드 작성, 디버깅, API 연동)  
        ✔ 웹 애플리케이션 프레임워크: Streamlit  
        """
        )
    with col2:
        pass
    with col3:
        if st.button("🔙 뒤로 가기"):
            st.session_state.page = "book_search"
            st.rerun()
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.header("🔍 사용된 기술")
    st.markdown(
        """
    - **개발언어**: Python
    - **요약 모델**: KoBART (소설 줄거리 요약가능하도록 파인 튜닝)
    - **문장 임베딩 검색 시스템**: FAISS (벡터 검색 시스템)
    - **데이터 출처**: 네이버 북 API
    - **웹 프레임워크**: Streamlit
    - **활용 API**:  
        - 네이버 북 API  
        - Google Drive API
    """
    )
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.header("데이터 수집 및 Kobart 활용 데이터 정제👾")
    st.markdown(
        """
    #### 1. **소설 데이터 수집**:  
    소설책의 줄거리 데이터를 수집하기 위해 다음과 같은 방법을 사용했습니다:  
    책의 줄거리만을 제공하는 책 API, 데이터 파일은 없었음  
    블로그 리뷰 크롤링: 개개인이 자유롭게 작성하는 블로그 양식 상 줄거리만을 크롭해 오기 어려움 + 개인 창작물로서의 저작권 문제
    챗지피티 이용: 대량의 책 데이터 줄거리를 API로 받아올 시 비용 문제 발생

    **[채택]👌 네이버 책 API**: 
    - **출판사에서 제공하는 책 소개글** 사용으로 저작권 문제 해결
    - author, title, description, image, publisher 등을 json 형식으로 데이터 제공받아 가공이 용이
    - 교보문고, 알라딘, 리디북스 등의 국내 서점 데이터를 통합 제공
    - **한국, 일본, 영미 소설**을 기준으로 검색하여 총 **1637권**의 책 정보를 수집.  

    **[한계] ✋네이버 API의 문제**:  
    Description에는 줄거리 뿐만 아니라 작가 연혁, 수상이력, 서평 등 이 포함됨.  
    줄거리만을 추출할 필요가 있었습니다.  

    ##### 📚 수집된 데이터 중 일부:
    """)
    prompt="""
    {
        "title": "겨울이 지나간 세계",
        "description": "“세상 불행의 표본 같은 남자, \n그에게 찾아온 기적 같은 겨울밤”\n\n인간의 상처에 대한 가슴 뭉클한 위로와 따뜻한 문장으로 인생의 아름다움을 조명해 온 소설가 아사다 지로의 신작이다.\n 2016년에서 2017년까지 1년간 일본 〈마이니치 신문〉에서 연재된 작품으로, 연재 내내 독자의 사랑을 받으며 ‘아사다 지로 감동 문학의 결정판’이라는 뜨거운 반응을 얻었다.\n\n\n정년퇴직을 맞이한 예순다섯 살의 다케와키는 송별회를 끝내고 집으로 돌아오는 길에 뇌출혈로 지하철에서 쓰러진다.\n 애틋한 가족과 잊었던 친구가 잇달아 병문안을 오던 그때, 병실에 누워 있던 다케와키에게 미스터리한 방문자들이 찾아온다.\n ‘마담 네즈’와 함께 병실을 빠져나가서 도쿄의 밤 풍경을 바라보며 고급스러운 저녁을 먹고, 갑자기 젊은 육체를 얻어 하얀색 선드레스를 입은 여인 ‘시즈카’와 한여름의 바닷가를 거닐기도 한다.\n 심지어 같은 처지의 옆 침대 환자 ‘가짱’과 같이 목욕탕에 갔다가 돌아오는 길에 포장마차 포렴 안에서 따뜻한 정종을 마시는 등 꿈도 망상도 아닌, 이세계(異世界)를 여행한다.\n \n\n그리고 기묘한 방문자들과 배회하며 이야기를 나누는 동안 겉보기엔 지적인 엘리트, 성공한 비즈니스맨 같았던 다케와키의 비극적인 과거, 불행으로 얼룩진 인생이 드러나는데….\n 일본 문단에서 가장 ‘탁월한 이야기꾼’이라 손꼽히는 작가답게 흥미진진한 환상 여행과 그 속에서 드러나는 진한 인생 이야기, 그리고 위로와 감동으로 눈물을 쏟게 하는 아사다 지로의 새로운 대표작이다.\n",
        "author": "아사다 지로"
    },
    {
        "title": "악마의 공놀이 노래",
        "description": "일본 본격 추리소설의 거장, 요코미조 세이시의 대표적 추리소설.\n\n\n소년탐정 김전일(긴다이치 하지메)의 할아버지, 긴다이치 코스케는 음울한 공놀이 노래가 떠도는 귀수촌에서, 연쇄 살인에 휘말린다.\n \n고립된 산 속의 마을, 패권을 나눠 가진 두 집안, 출생의 비밀, 노래에 맞춰 일어나는 사건 그리고 명탐정이 풀어가는 사건 등 흥미진진한 소재를 재치있는 입담으로 풀어내고 있다.\n \n\n때는 쇼와 30년(1955년).\n 당시 근방을 혼란으로 몰아넣은 '옥문도', '팔묘촌' 사건을 마음속에 간직한 채, 긴다이치 코스케는 요양 차 다시 오카야마 현을 찾는다.\n 그리고 귀수촌 마을의 한적한 온천 거북탕에서 이소카와 경부와 재회하고, 23년 전 마을을 떠들썩케 한 사건의 자초지종을 듣는다.\n\n\n큰 명절 준비에 여념이 없는 귀수촌.\n 하지만 비밀을 간직한 듯한 촌장이 행방불명되고, 일본 최고의 인기 여배우가 된 오조라 유카리가 마을로 돌아오면서 불안한 기운은 더욱 짙어간다.\n 이윽고 축제 자리, 그녀의 단짝 친구였던 여인들이 저주스러운 공놀이 노래에 맞춰 한 명씩 연쇄 살인에 휘말리는데….\n",
        "author": "요코미조 세이시"
    },"""
    st.code(prompt, language="json")
    st.markdown("---")
    st.markdown(
            """
        #### 2. **데이터 정제를 위한 Kobart 모델 파인튜닝**:  
        **description**에서 다른 부가적인 정보는 제외하고 **줄거리**만을 요약 하기위해,  
        뉴스 요약에 특화된 **BART 모델** 중 한국어 요약에 최적화된 **KoBART** 모델을 사용하였으며,  
        1637권 중 300권을 랜덤으로 추출하여 수상, 작가 연혁, 서평 등 책 설명의 부가적인 정보는 제외하고, **줄거리**만을 요약하여 라벨링한 후 파인튜닝을 진행했습니다.  
        에포크는 5회 진행, 그 중 오버튜닝 가능성이 가장 적은 에포크 2 모델을 채택하여 줄거리 요약을 진행했습니다.  
        책 설명에 줄거리가 없는 책은 제외하여 총 1322권의 책 데이터를 준비했습니다.
        [👾Kobart 모델](https://huggingface.co/gogamza/kobart-summarization)  
        """)
    st.image("image/sc_1.png", width=500)

    st.markdown("""
    ##### 📚 정제된 데이터 중 일부:
    """)
    prompt="""
        {
        "title": "겨울이 지나간 세계",
        "description": "“세상 불행의 표본 같은...하는 아사다 지로의 새로운 대표작이다.\n",
        "author": "아사다 지로",
        ////-----👇[요약한 줄거리]-----
        "summary": "예순다섯 살의 다케와키가 뇌출혈로 쓰러진 후 기묘한 방문자들과 배회하며 이야기를 나누는 동안, \n 겉보기엔 지적인 엘리트, 성공한 비즈니스맨 같았던 다케와키의 비극적인 과거와 불행으로 얼룩진 인생이 드러나게 된다. \n 소설가 아사다 지로의 신작."
        ////-----👆[요약한 줄거리]-----
    },
    {
        "title": "악마의 공놀이 노래",
        "description": "일본 본격 추리소설의 거장, ... 단짝 친구였던 여인들이 저주스러운 공놀이 노래에 맞춰 한 명씩 연쇄 살인에 휘말리는데….\n",
        "author": "요코미조 세이시",
        ////-----👇[요약한 줄거리]-----
        "summary": "소년탐정 김전일(긴다이치 하지메)의 할아버지, \n 긴다이치 코스케는 음울한 공놀이 노래가 떠도는 귀수촌에서 연쇄 살인에 휘말린다. \n 연쇄 살인으로 휘말리는 이 마을에는 촌장이 행방불명되고, \n 일본 최고의 인기 여배우가 된 오조라 유카리가 마을로 돌아오면서 불안한 기운은 더욱 짙어지고, \n 이윽고 축제 자리, 그녀의 단짝 친구였던 여인들이 연쇄 살인에 휘말린다. \n 연쇄 살인에 휘말리는 소녀들은 저주스러운 공놀이 노래에 맞춰 한 명씩 연쇄 살인에 휘말린다. \n 연쇄 살인에 휘말리는 소녀들은 연쇄 살인의 흔적을 추적하며 긴장감을 높인다."
        ////-----👆[요약한 줄거리]-----
    },
    """
    st.code(prompt, language="json")
    st.markdown("---")
    st.header("FAISS 라이브러리 검색 시스템 완성👾")
    st.markdown(
        """
    #### 3. **FAISS 기반 검색 시스템 구축**:  
    KoBART로 description에서 summary를 정제한 1322권의 책 데이터를 토대로,  
    책 줄거리의 유사도를 계산하기 위해 KoSimCSE-roberta 임베딩 모델을 사용하여 **FAISS** 검색 시스템 구현, 
    **코사인 유사도**를 기준으로 인덱싱하여 유저가 입력한 줄거리와 유사한 책을 빠르게 찾아낼 수 있도록 했습니다.
    [🗂️FAISS 임베딩모델](https://huggingface.co/BM-K/KoSimCSE-roberta)
    """)
    st.markdown("---")
    st.markdown(
        """
    #### 4. **유저 피드백 반영**:  
    유저가 책 제목을 찾지 못했을 경우, **구글 검색**을 통해 해당 책의 정보를 검색할 수 있도록 시스템을 설계했습니다.  
    또한, 유저의 피드백을 통해 데이터베이스를 지속적으로 보강할 수 있도록 설계하였습니다.
    """
    )

    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.subheader("StreamlitApp 배포 과정👾")
    st.markdown(
        """
        1. **로컬 컴퓨터 작업:**  
        - 코드 개발 및 테스트
        - 유저가 입력한 줄거리를 임베딩 후 인덱스에서 검색 되도록 설계
        - 책 제목을 검색 후 네이버 Book API에서 상세 줄거리를 받아오도록 함
        - 유저의 피드백을 requirements.txt에 저장할 수 있도록 함
        2. **스트림릿 배포:**  
        - **requirements.txt**으로 필요한 라이브러리 목록 관리
        - GitHub에 최종 푸쉬 후 스트림릿에 연동
        - 유저의 피드백을 확인, 관리할 수 있도록 구글 드라이브에 저장되도록 API 등록
        """
    )
    st.markdown(
        """
    <hr style="border: 1px solid gray; margin-top: 20px; margin-bottom: 20px;">
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    ## 📞 **문의**
    - Email: marurun66@gmail.com
    - GitHub: [https://github.com/marurun66](https://github.com/marurun66/book-publication)
    """
    )
    st.markdown(
        """
    ### 
    """
    )