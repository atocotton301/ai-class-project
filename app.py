import streamlit as st
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="HanS-Plan AI",
    page_icon="📅",
    layout="centered"
)

# 졸업 요건 상정 (상수 설정)
GRADUATION_POINTS = 800

# 세션 상태 초기화 (데이터 유지 및 연동용)
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

st.title("📅 HanS-Plan AI")
st.subheader("한성대 비교과 스마트 내비게이터 온보딩")
st.write(f"반가워요! 졸업 필수 요건인 **비교과 마일리지 {GRADUATION_POINTS}점**을 효율적으로 달성하기 위한 맞춤형 학적 정보를 설정해 주세요.")

# --- 데이터 사전 정의 (한성대 공식 학과 및 학과별 추천 자격증 매핑) ---
cert_mapping = {
    "AI응용학과": ["정보처리기사", "AWS Certified Cloud Practitioner", "SQLD (SQL개발자)", "ADsP (데이터분석준전문가)", "TOPCIT"],
    "컴퓨터공학부": ["정보처리기사", "리눅스마스터 1급/2급", "네트워크관리사", "정보보안기사", "CCNA", "TOPCIT"],
    "IT융합공학부": ["정보처리기사", "정보통신기사", "임베디드기사", "무선설비기사", "TOPCIT"],
    "기계전자공학부": ["일반기계기사", "전기기사", "전자기사", "기계설계기사", "산업안전기사"],
    "사회과학부 (경영/행정/무역 등)": ["전산세무회계", "매경TEST", "공인회계사(CPA)", "공인노무사", "유통관리사/물류관리사"],
    "크리에이티브인문학부": ["한국사능력검정시험", "관광통역안내사", "사서자격증", "컴퓨터활용능력 1급/2급"],
    "예술학부 / 글로벌패션산업학부": ["GTQ 그래픽기술자격", "컴퓨터그래픽스운용기능사", "컬러리스트기사", "패션디자인산업기사"],
    "상상력인재학부 (자율전공)": ["컴퓨터활용능력 1급/2급", "MOS Master", "TOEIC / 오픽(OPIc)", "정보기술자격(ITQ)"]
}

# 한성대 스마트자기관리시스템(hsportal) 공식 역량 및 유형별 분류
hsportal_categories = [
    "자기주도역량 프로그램 (리더십, 자아탐색, 학습법 등)",
    "소통협력역량 프로그램 (팀워크, 커뮤니케이션, 협동심 등)",
    "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)",
    "글로벌역량 프로그램 (어학, 교환학생, 다문화 이해 등)",
    "취·창업 지원 프로그램 (포트폴리오, 면접 컨설팅, 창업 동아리)",
    "학습인프라/학습법 강화 (학습 튜터링, 상상부기 피어코칭)",
    "사회봉사 및 인성 함양 (교내외 봉사활동, 멘토링 프로그램)"
]

# --- 화면 레이아웃 시작 ---

# [1단계] 학적 및 구글 계정 정보
st.write("### 🔐 1. 학적 및 인증 정보 설정")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("👤 이름", placeholder="조선기")
with col2:
    student_id = st.text_input("🆔 학번 (7자리)", placeholder="2410001", max_chars=7)
    
user_email = st.text_input(
    "📧 구글 이메일 (@gmail.com 필수)", 
    placeholder="username@gmail.com",
    help="비교과 마감 임박 알림 수신 및 로그인 세션 연동에 사용됩니다."
)

st.markdown("---")

# [2단계] 학과 선택 및 실시간 자격증 연동 (Dynamic Selectbox 적용)
st.write("### 🎯 2. 소속 학과 및 목표 자격증 설정")
selected_major = st.selectbox(
    "소속 학과(학부)를 선택해 주세요",
    list(cert_mapping.keys())
)

# 선택한 학과에 맞춰 자격증 옵션이 드롭아웃 형태로 바뀜
available_certs = cert_mapping[selected_major]
selected_certs = st.multiselect(
    f"💡 {selected_major} 유저들이 선호하는 자격증 목록입니다 (복수 선택 가능)",
    options=available_certs,
    default=None
)

st.markdown("---")

# [3단계] 스마트자기관리시스템 기반 마일리지 및 관심사 설정
st.write("### 📊 3. 비교과 목표 및 현재 마일리지 현황")

# 현재 얻은 점수 입력칸
current_points = st.number_input(
    "🏁 현재까지 취득한 누적 비교과 포인트", 
    min_value=0, 
    max_value=GRADUATION_POINTS, 
    value=0, 
    step=5,
    help="스마트자기관리시스템(hsportal) 내 마이페이지에서 확인 가능한 현재 점수를 적어주세요."
)

# 이번 학기 목표 점수 설정 (5점 단위 슬라이더 필수 충족)
target_points = st.slider(
    "📈 이번 학기 목표 비교과 포인트", 
    min_value=0, 
    max_value=200, 
    value=30, 
    step=5
)

# hsportal 분류 항목 다중 선택
selected_categories = st.multiselect(
    "🔍 우선적으로 추천받고 싶은 비교과 분야를 선택해 주세요",
    options=hsportal_categories
)

# 졸업 요건 도달률 시각화 대시보드 미리보기
remaining_points = GRADUATION_POINTS - current_points
progress_percent = min(current_points / GRADUATION_POINTS, 1.0)

st.write("#### 🎓 나의 졸업 비교과 요건 도달 현황")
st.progress(progress_percent)
if remaining_points <= 0:
    st.success(f"🎉 축하합니다! 졸업 요건({GRADUATION_POINTS}점)을 완전히 충족하셨습니다!")
else:
    st.info(f"💡 졸업 점수까지 **{remaining_points}점** 남았습니다. (현재 진행률: {progress_percent*100:.1f}%)")

# --- 최종 저장 버튼 활성화 및 벨리데이션 ---
st.markdown(" ")
if st.button("인증 및 프로필 설정 완료 🚀", use_container_width=True):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    
    if not user_name or not student_id or not user_email:
        st.error("⚠️ 이름, 학번, 이메일은 필수 입력 사항입니다.")
    elif not student_id.isdigit() or len(student_id) != 7:
        st.error("⚠️ 학번은 7자리 숫자여야 합니다. (예: 2410001)")
    elif not re.match(email_pattern, user_email):
        st.error("⚠️ 반드시 올바른 Gmail 주소(@gmail.com)를 입력해야 합니다.")
    elif not selected_categories:
        st.error("⚠️ 관심 있는 비교과 분야를 최소 1개 이상 선택해 주세요.")
    else:
        # 데이터 최종 바인딩
        st.session_state.user_profile = {
            "name": user_name,
            "student_id": student_id,
            "email": user_email,
            "major": selected_major,
            "certifications": selected_certs,
            "current_points": current_points,
            "target_points": target_points,
            "categories": selected_categories
        }
        st.session_state.is_logged_in = True
        
        st.success(f"🎉 {user_name}님의 한성대 학적 계정 연동 및 AI 네비게이션 프로필 설정이 완전히 완료되었습니다!")
        st.balloons()