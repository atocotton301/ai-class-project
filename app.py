import streamlit as st
import re
import json
import os

USERS_DB_PATH = "data/users_db.json"

def load_users():
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user(user_id, password):
    os.makedirs("data", exist_ok=True)
    users = load_users()
    users[user_id] = password
    with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
        
# ==========================================
# 1. 시스템 초기화 및 페이지 전역 설정
# ==========================================
st.set_page_config(
    page_title="HanS-Plan AI",
    page_icon="📅",
    layout="centered"
)

# 졸업 요건 및 시스템 상수 설정
GRADUATION_POINTS = 800
USERS_DB_PATH = "data/users_db.json"
PROFILE_DB_PATH = "data/user_profile.json"

# 세션 상태(Session State) 안정화 아키텍처
if 'app_step' not in st.session_state:
    st.session_state.app_step = 'login_signup'  # 최초 진입 단계를 로그인/회원가입으로 지정
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# ==========================================
# 2. 백엔드 데이터 입출력(I/O) 함수 정의
# ==========================================
def load_users():
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user(user_id, password):
    os.makedirs("data", exist_ok=True)
    users = load_users()
    users[user_id] = password
    with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_profile_from_file():
    if os.path.exists(PROFILE_DB_PATH):
        with open(PROFILE_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ==========================================
# 3. 화면 렌더링 파이프라인 (라우팅 제어)
# ==========================================

# ------------------------------------------
# [STEP 1] 로그인 및 회원가입 인증 화면
# ------------------------------------------
if st.session_state.app_step == 'login_signup':
    st.title("🚀 HanS-Plan AI 시작하기")
    
    # 탭 메뉴 아키텍처를 통한 Front-End 공간 효율화
    tab_login, tab_signup = st.tabs(["🔑 기존 계정 로그인", "📝 새 계정 회원가입"])
    
    # 1-1. 로그인 처리 로직
    with tab_login:
        st.subheader("로그인")
        with st.container(border=True):
            login_id = st.text_input("아이디", placeholder="아이디를 입력하세요", key="login_id_input")
            login_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_pw_input")
            
            if st.button("로그인 🚀", use_container_width=True):
                users_db = load_users()
                if not login_id or not login_pw:
                    st.error("⚠️ 아이디와 비밀번호를 모두 입력해 주세요.")
                elif login_id in users_db and users_db[login_id] == login_pw:
                    # 데이터 정합성 검증 성공 시 세션 동기화 후 대시보드 직행
                    st.session_state.is_logged_in = True
                    # 기존 저장된 프로필이 있다면 세션에 로드
                    saved_profile = load_profile_from_file()
                    if saved_profile:
                        st.session_state.user_profile = saved_profile
                    st.session_state.app_step = 'main'
                    st.rerun()
                else:
                    st.error("❌ 아이디가 존재하지 않거나 비밀번호가 틀렸습니다.")

    # 1-2. 회원가입 처리 로직
    with tab_signup:
        st.subheader("계정 생성")
        with st.container(border=True):
            new_id = st.text_input("아이디 설정", placeholder="사용할 아이디를 입력하세요", key="new_id_input")
            new_pw = st.text_input("비밀번호 설정", type="password", placeholder="사용할 비밀번호를 입력하세요", key="new_pw_input")
            
            if st.button("가입하고 프로필 설정하러 가기 ➡️", use_container_width=True):
                users_db = load_users()
                if not new_id or not new_pw:
                    st.error("⚠️ 아이디와 비밀번호를 모두 입력해 주세요.")
                elif new_id in users_db:
                    st.error("⚠️ 이미 존재하는 아이디입니다. 다른 아이디를 입력해 주세요.")
                else:
                    # 회원가입 성공 시 파일 DB에 영구 적재 후 온보딩 유도
                    save_user(new_id, new_pw)
                    st.session_state.app_step = 'onboarding'
                    st.rerun()

# ------------------------------------------
# [STEP 2] 온보딩 프로필 설정 화면 (제공 코드 정밀 결합)
# ------------------------------------------
elif st.session_state.app_step == 'onboarding':
    st.title("📅 HanS-Plan AI")
    st.subheader("한성대 비교과 스마트 내비게이터 온보딩")
    st.write(f"반가워요! 졸업 필수 요건인 **비교과 마일리지 {GRADUATION_POINTS}점**을 효율적으로 달성하기 위한 맞춤형 학적 정보를 설정해 주세요.")

    # 학과별 전공 자격증 딕셔너리 사전 정의
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

    # 2-1. 학적 및 구글 계정 정보 입력 컴포넌트
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

    # 2-2. 전공 특화 및 공통 자격증 분리 UI
    st.write("### 🎯 2. 소속 학과 및 목표 자격증 설정")
    selected_major = st.selectbox("소속 학과(학부)를 선택해 주세요", list(cert_mapping.keys()))

    st.markdown(f"**💡 {selected_major} 전공 특화 자격증**")
    major_certs = st.multiselect(
        "전공 관련 자격증을 선택해 주세요 (복수 선택 가능)",
        options=cert_mapping[selected_major],
        key=f"major_certs_{selected_major}"
    )

    st.markdown("**💡 공통 필수/선택 자격증**")
    base_certs = st.multiselect("어학 및 공통 자격증을 선택해 주세요 (복수 선택 가능)", options=common_certs)

    st.markdown("---")

    # 2-3. 마일리지 공식 규정 계산기 및 대시보드 시각화
    st.write("### 📊 3. 비교과 목표 및 현재 마일리지 현황")
    current_points = st.number_input(
        "🏁 현재까지 취득한 누적 비교과 포인트", 
        min_value=0, max_value=GRADUATION_POINTS, value=0, step=5,
        help="스마트자기관리시스템(hsportal) 내 마이페이지에서 확인 가능한 현재 점수를 적어주세요."
    )

    remaining_points = GRADUATION_POINTS - current_points
    progress_percent = min(current_points / GRADUATION_POINTS, 1.0)

    st.write("#### 🎓 나의 졸업 비교과 요건 도달 현황")
    st.progress(progress_percent)
    if remaining_points <= 0:
        st.success(f"🎉 축하합니다! 졸업 요건({GRADUATION_POINTS}점)을 완전히 충족하셨습니다!")
    else:
        st.info(f"💡 졸업 점수까지 **{remaining_points}점** 남았습니다. (현재 진행률: {progress_percent*100:.1f}%)")

    st.markdown("---")

    target_points = st.slider("📈 이번 학기 목표 비교과 포인트", min_value=0, max_value=800, value=150, step=5)

    # 한성대 공식 배점 로직 연산
    recognized_points = min(target_points, 200)                             
    carryover_points = min(max(target_points - 200, 0), 200)                
    expired_points = max(target_points - 400, 0)                             
    expected_total_points = current_points + recognized_points

    st.write("##### 💡 목표 달성 시 포인트 정산 예측")
    st.caption("한 학기당 인정 포인트 200점 / 다음 학기 이월 포인트 최대 200점 / 400점 초과 시 나머지 획득 포인트는 소멸")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔮 최종 예상 포인트", f"{expected_total_points}점", f"+{recognized_points}점 합산")
    c2.metric("이번 학기 인정", f"{recognized_points}점", "최대 한도" if recognized_points == 200 else None)
    c3.metric("다음 학기 이월", f"{carryover_points}점", "최대 한도" if carryover_points == 200 else None)

    if expired_points > 0:
        c4.metric("⚠️ 소멸 예정", f"{expired_points}점", "-초과분 소멸", delta_color="inverse")
        st.warning(f"🚨 **주의:** 한 학기 인정 및 이월 규정 한도(총 400점)를 초과하여 **{expired_points}점**이 소멸됩니다.")
    else:
        c4.metric("✅ 소멸 예정", "0점")

    st.markdown(" ")
    selected_categories = st.multiselect("🔍 우선적으로 추천받고 싶은 비교과 분야를 선택해 주세요", options=hsportal_categories)

    # 2-4. 예외 벨리데이션(Validation) 및 파일 영구 적재
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
            # 상태값 및 패키징 데이터 동기화
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
            st.session_state.app_step = 'main'
            
            # JSON 데이터 파이프라인 구축 (물리적 파일 쓰기)
            os.makedirs("data", exist_ok=True)
            with open(PROFILE_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(st.session_state.user_profile, f, ensure_ascii=False, indent=4)
            
            st.success(f"🎉 {user_name}님의 프로필 설정이 완료되었습니다!")
            st.balloons()
            st.rerun()

# ------------------------------------------
# [STEP 3] 로그인 및 인증 완료 후 메인 랜딩 대시보드
# ------------------------------------------
elif st.session_state.app_step == 'main':
    st.title(f"👋 반갑습니다, {st.session_state.user_profile.get('name', '사용자')}님!")
    st.success("인증 시스템 및 매주 맞춤형 크롤링 파이프라인이 정상적으로 가동 중입니다.")
    
    with st.container(border=True):
        st.write("### 📊 나의 현황 요약 요약")
        st.write(f"소속 전공: **{st.session_state.user_profile.get('major')}**")
        st.write(f"현재 달성 마일리지: **{st.session_state.user_profile.get('current_points')} pt** / {GRADUATION_POINTS} pt")
        st.write(f"예상 최종 마일리지: **{st.session_state.user_profile.get('expected_total_points')} pt**")
        st.write(f"설정된 관심 분야 개수: **{len(st.session_state.user_profile.get('categories', []))}개**")

    if st.button("안전한 로그아웃 🔓", use_container_width=True):
        st.session_state.app_step = 'login_signup'
        st.session_state.is_logged_in = False
        st.session_state.user_profile = {}
        st.rerun()
