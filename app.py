import streamlit as st
import re
import json
import os

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

# --- 데이터 사전 정의 ---
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

# 🛠️ [요청 반영] 공통 자격증 리스트 분리 (비교과 배점 디테일 포함)
common_certs = ["TOEIC (비교과 10pt)", "OPIc/영어말하기", "컴퓨터활용능력 1급", "컴퓨터활용능력 2급", "한국사능력검정시험", "ITQ(정보기술자격)"]

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
    user_name = st.text_input("👤 이름", placeholder="김한성")
with col2:
    student_id = st.text_input("🆔 학번 (7자리)", placeholder="2610001", max_chars=7)
    
user_email = st.text_input(
    "📧 구글 이메일 (@gmail.com 필수)", 
    placeholder="username@gmail.com",
    help="비교과 마감 임박 알림 수신 및 로그인 세션 연동에 사용됩니다."
)

st.markdown("---")

# [2단계] 학과 선택 및 실시간 자격증 연동
st.write("### 🎯 2. 소속 학과 및 목표 자격증 설정")
selected_major = st.selectbox(
    "소속 학과(학부)를 선택해 주세요",
    list(cert_mapping.keys())
)

# 🛠️ [요청 반영] 전공 특화 자격증과 공통 자격증 UI 이원화
st.markdown(f"**💡 {selected_major} 전공 특화 자격증**")
major_certs = st.multiselect(
    "전공 관련 자격증을 선택해 주세요 (복수 선택 가능)",
    options=cert_mapping[selected_major],
    key=f"major_certs_{selected_major}" # 학과 변경 시 안전하게 리렌더링되도록 key 부여
)

st.markdown("**💡 공통 필수/선택 자격증**")
base_certs = st.multiselect(
    "어학 및 공통 자격증을 선택해 주세요 (복수 선택 가능)",
    options=common_certs
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

# 누적 포인트 바로 아래에 도달 현황 배치
remaining_points = GRADUATION_POINTS - current_points
progress_percent = min(current_points / GRADUATION_POINTS, 1.0)

st.write("#### 🎓 나의 졸업 비교과 요건 도달 현황")
st.progress(progress_percent)
if remaining_points <= 0:
    st.success(f"🎉 축하합니다! 졸업 요건({GRADUATION_POINTS}점)을 완전히 충족하셨습니다!")
else:
    st.info(f"💡 졸업 점수까지 **{remaining_points}점** 남았습니다. (현재 진행률: {progress_percent*100:.1f}%)")

st.markdown("---")

# 이번 학기 목표 점수 설정
target_points = st.slider(
    "📈 이번 학기 목표 비교과 포인트", 
    min_value=0, 
    max_value=800, 
    value=150, 
    step=5
)

# 한성대 공식 마일리지 규정 자동 계산 비즈니스 로직
recognized_points = min(target_points, 200)                             
carryover_points = min(max(target_points - 200, 0), 200)                
expired_points = max(target_points - 400, 0)                             
expected_total_points = current_points + recognized_points

st.write("##### 💡 목표 달성 시 포인트 정산 예측")
st.caption("한 학기당 인정 포인트 200점 / 다음 학기 이월 포인트 최대 200점 / 400점 초과 시 나머지 획득 포인트는 소멸")

# 대시보드 레이아웃 4칸 구성
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔮 최종 예상 포인트", f"{expected_total_points}점", f"+{recognized_points}점 합산")
c2.metric("이번 학기 인정", f"{recognized_points}점", "최대 한도" if recognized_points == 200 else None)
c3.metric("다음 학기 이월", f"{carryover_points}점", "최대 한도" if carryover_points == 200 else None)

if expired_points > 0:
    c4.metric("⚠️ 소멸 예정", f"{expired_points}점", "-초과분 소멸", delta_color="inverse")
    st.warning(f"🚨 **주의:** 한 학기 인정 및 이월 규정 한도(총 400점)를 초과하여 **{expired_points}점**이 그대로 소멸됩니다. 효율적인 일정 수립을 권장합니다.")
else:
    c4.metric("✅ 소멸 예정", "0점")

st.markdown(" ")

# hsportal 분류 항목 다중 선택
selected_categories = st.multiselect(
    "🔍 우선적으로 추천받고 싶은 비교과 분야를 선택해 주세요",
    options=hsportal_categories
)

# --- 최종 저장 버튼 활성화 및 벨리데이션 ---
st.markdown(" ")
if st.button("인증 및 프로필 설정 완료 🚀", use_container_width=True):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    
    if not user_name or not student_id or not user_email:
        st.error("⚠️ 이름, 학번, 이메일은 필수 입력 사항입니다.")
    elif not student_id.isdigit() or len(student_id) != 7:
        st.error("⚠️ 학번은 7자리 숫자여야 합니다. (예: 2610001)")
    elif not re.match(email_pattern, user_email):
        st.error("⚠️ 반드시 올바른 Gmail 주소(@gmail.com)를 입력해야 합니다.")
    elif not selected_categories:
        st.error("⚠️ 관심 있는 비교과 분야를 최소 1개 이상 선택해 주세요.")
    else:
        # 🛠️ [요청 반영] 사용자가 선택한 전공 자격증과 공통 자격증을 합쳐서 저장
        combined_certs = major_certs + base_certs
        
        st.session_state.user_profile = {
            "name": user_name,
            "student_id": student_id,
            "email": user_email,
            "major": selected_major,
            "certifications": combined_certs,
            "current_points": current_points,
            "target_points": target_points,
            "recognized_points": recognized_points,
            "carryover_points": carryover_points,
            "expired_points": expired_points,
            "expected_total_points": expected_total_points,
            "categories": selected_categories
        }
        st.session_state.is_logged_in = True
        
        # 💡 팀원 연동을 위한 JSON 물리 파일 자동 생성 로직 유지
        os.makedirs("data", exist_ok=True)
        file_path = "data/user_profile.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.user_profile, f, ensure_ascii=False, indent=4)
        
        st.success(f"🎉 {user_name}님의 프로필 설정이 완료되었으며, 팀원 연동(data/user_profile.json) 데이터가 무사히 저장되었습니다!")
        st.balloons()