import streamlit as st

# 페이지 기본 설정 (가장 위에 와야 함)
st.set_page_config(
    page_title="HanS-Plan AI",
    page_icon="📅",
    layout="centered"
)

# 세션 상태 초기화 (데이터 저장을 위함)
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

st.title("📅 HanS-Plan AI")
st.subheader("한성대 비교과 스마트 내비게이터 온보딩")
st.write("환영합니다! 맞춤형 비교과 추천을 위해 프로필을 설정해 주세요.")

# 온보딩 입력 폼 생성
with st.form("onboarding_form"):
    st.write("#### 👤 기본 정보 설정")
    
    # 1. 학과 선택
    major = st.selectbox(
        "소속 학과를 선택해 주세요",
        ["AI응용학과", "컴퓨터공학부", "기계전자공학부", "IT융합공학부", "문학문화콘텐츠학과", "경영학과"]
    )
    
    # 2. 관심 분야 다중 선택
    interests = st.multiselect(
        "관심 있는 비교과 분야를 모두 골라주세요",
        ["웹/앱개발", "인공지능/데이터", "디자인/UX", "어학/교환학생", "창업/공모전", "봉사활동"]
    )
    
    # 3. 목표 자격증
    certifications = st.multiselect(
        "이번 학기 목표 자격증이 있나요?",
        ["정보처리기사", "정보처리산업기사", "TOPCIT", "ITQ", "리눅스마스터", "해당 없음"]
    )
    
    # 4. 목표 포인트 설정
    target_points = st.slider("이번 학기 목표 하이업(비교과) 포인트", 0, 100, 30)
    
    # 제출 버튼
    submitted = st.form_submit_button("설정 완료하고 캘린더로 이동 🚀")
    
    if submitted:
        # 입력받은 데이터 세션에 저장
        st.session_state.user_profile = {
            "major": major,
            "interests": interests,
            "certifications": certifications,
            "target_points": target_points
        }
        st.success("프로필 설정이 완료되었습니다! (추후 캘린더 페이지로 자동 이동됩니다)")
        st.balloons() # 도파민용 풍선 효과 🎉