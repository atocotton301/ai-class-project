import streamlit as st
import pandas as pd
import json
import os

st.title("👤 마이페이지")

# 1. 로그인 및 온보딩 여부 검증
if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면에서 온보딩을 먼저 완료해 주세요.")
    st.stop()

DATA_PATH = "data/user_profile.json"

# 2. 프로필 입출력 함수 정의
def load_profile():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_profile(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

profile = load_profile()

if profile:
    # 수정 모드 상태 초기화
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    st.subheader(f"**{profile.get('name')}** 님의 개인 공간")
    
    # 🎯 탭(Tab)을 활용하여 프로필과 시간표 화면 분리
    tab_profile, tab_timetable = st.tabs(["👤 기본 프로필 관리", "📅 정규 시간표 관리"])

    # =========================================================
    # [TAB 1] 프로필 조회 및 수정 모드
    # =========================================================
    with tab_profile:
        # 화면 분기 1: 프로필 조회 모드
        if not st.session_state.edit_mode:
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image("https://via.placeholder.com/150", caption="프로필 이미지")
                with col2:
                    st.write(f"**이름:** {profile.get('name')}")
                    st.write(f"**학번:** {profile.get('student_id')}")
                    st.write(f"**전공:** {profile.get('major')}")
                    st.write(f"**이메일:** {profile.get('email')}")

            st.write("### 🏆 비교과 포인트 달성도")
            curr = profile.get('current_points', 0)
            total_expected = profile.get('expected_total_points', 0)
            
            st.progress(min(curr / 800, 1.0))
            c1, c2 = st.columns(2)
            c1.metric("현재 포인트", f"{curr} pt")
            c2.metric("목표 달성 시 예상", f"{total_expected} pt")

            col_a, col_b = st.columns(2)
            with col_a:
                st.write("#### 🔍 관심 카테고리")
                for cat in profile.get('categories', []):
                    st.write(f"- {cat}")
            with col_b:
                st.write("#### 📜 목표 자격증")
                for cert in profile.get('certifications', []):
                    st.write(f"- {cert}")

            st.markdown("---")
            if st.button("프로필 수정하기", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
                
        # 화면 분기 2: 프로필 수정 모드
        else:
            st.markdown("### 📝 프로필 수정하기")
            
            # 학과 데이터 및 카테고리 매핑 구조 정의
            cert_mapping = {
                "AI응용학과": ["정보처리기사", "AWS Certified Cloud Practitioner", "SQLD", "ADsP", "TOPCIT"],
                "컴퓨터공학부": ["정보처리기사", "리눅스마스터", "네트워크관리사", "정보보안기사", "CCNA"],
                "IT융합공학부": ["정보처리기사", "정보통신기사", "임베디드기사", "무선설비기사"],
                "기계전자공학부": ["일반기계기사", "전기기사", "전자기사", "기계설계기사"],
                "사회과학부 (경영/행정/무역 등)": ["전산세무회계", "매경TEST", "CPA", "공인노무사"],
                "크리에이티브인문학부": ["한국사", "관광통역", "사서", "컴활 1급/2급"],
                "예술학부 / 글로벌패션산업학부": ["GTQ", "컴퓨터그래픽스", "컬러리스트", "패션디자인"],
                "상상력인재학부 (자율전공)": ["컴활 1급/2급", "MOS Master", "TOEIC / 오픽", "ITQ"]
            }
            common_certs = ["TOEIC (비교과 10pt)", "OPIc/영어말하기", "컴퓨터활용능력 1급", "컴퓨터활용능력 2급", "한국사능력검정시험", "ITQ"]
            hsportal_categories = [
                "자기주도역량 프로그램", "소통협력역량 프로그램", "창의융합역량 프로그램",
                "글로벌역량 프로그램", "취·창업 지원 프로그램", "학습인프라/학습법 강화", "사회봉사 및 인성 함양"
            ]

            # 데이터 일괄 수정을 위한 Form 컴포넌트 구성
            with st.form("edit_profile_form"):
                edited_name = st.text_input("이름", value=profile.get('name'))
                edited_email = st.text_input("이메일", value=profile.get('email'))
                
                majors = list(cert_mapping.keys())
                default_major_idx = majors.index(profile.get('major')) if profile.get('major') in majors else 0
                edited_major = st.selectbox("소속 학과", majors, index=default_major_idx)
                
                current_certs = profile.get('certifications', [])
                default_major_certs = [c for c in current_certs if c in cert_mapping.get(edited_major, [])]
                default_base_certs = [c for c in current_certs if c in common_certs]
                
                edited_major_certs = st.multiselect(f"💡 {edited_major} 전공 자격증", options=cert_mapping[edited_major], default=default_major_certs)
                edited_base_certs = st.multiselect("💡 공통 자격증", options=common_certs, default=default_base_certs)
                
                default_cats = [c for c in profile.get('categories', []) if c in hsportal_categories]
                edited_categories = st.multiselect("🔍 관심 비교과 분야", options=hsportal_categories, default=default_cats)
                
                edited_current_points = st.number_input("🏁 현재 취득 포인트", min_value=0, max_value=800, value=int(profile.get('current_points', 0)), step=5)
                edited_target_points = st.slider("📈 이번 학기 목표 포인트", 0, 800, value=int(profile.get('target_points', 150)))
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    save_submitted = st.form_submit_button("변경 사항 저장", use_container_width=True)
                with col_btn2:
                    cancel_submitted = st.form_submit_button("수정 취소", use_container_width=True)
                    
                if save_submitted:
                    if not edited_name or not edited_email or not edited_categories:
                        st.error("필수 정보를 누락 없이 입력해 주세요.")
                    else:
                        new_recognized = min(edited_target_points, 200)
                        new_expected_total = edited_current_points + new_recognized
                        
                        # 🚨 주의: 기존에 저장된 timetable 데이터가 날아가지 않도록 유지!
                        updated_profile = {
                            "name": edited_name,
                            "student_id": profile.get('student_id'),
                            "email": edited_email,
                            "major": edited_major,
                            "certifications": edited_major_certs + edited_base_certs,
                            "current_points": edited_current_points,
                            "target_points": edited_target_points,
                            "categories": edited_categories,
                            "expected_total_points": new_expected_total,
                            "timetable": profile.get('timetable', [])  # 시간표 데이터 보존
                        }
                        
                        save_profile(updated_profile)
                        st.session_state.user_profile = updated_profile
                        st.session_state.edit_mode = False
                        st.success("프로필 수정이 완료되었습니다.")
                        st.rerun()
                        
                if cancel_submitted:
                    st.session_state.edit_mode = False
                    st.rerun()

    # =========================================================
    # [TAB 2] 정규 시간표 입력 및 수정 
    # =========================================================
    with tab_timetable:
        st.markdown("### 🏫 나의 정규 수업 시간표")
        st.caption("비교과 프로그램 신청 시 **수업 시간 겹침 경고 알림**을 받기 위해 정확히 입력해 주세요.")
        st.caption("💡 표의 마지막 줄을 클릭하여 과목을 추가하거나, 가장 왼쪽을 클릭하고 'Delete'를 눌러 삭제할 수 있습니다.")

        # 1. 프로필 데이터에 시간표(timetable) 키가 없으면 빈 리스트로 초기화
        if "timetable" not in profile:
            profile["timetable"] = []

        # 2. DataFrame으로 변환 (UI 출력을 위해)
        if len(profile["timetable"]) > 0:
            df_timetable = pd.DataFrame(profile["timetable"])
        else:
            # 빈 시간표일 경우 기본 구조 생성
            df_timetable = pd.DataFrame(columns=["요일", "과목명", "시작시간", "종료시간"])

        # 3. 시간대 선택을 위한 리스트 생성 (09:00 ~ 21:00)
        time_options = [f"{str(h).zfill(2)}:{str(m).zfill(2)}" for h in range(9, 22) for m in (0, 30)]

        # 4. st.data_editor 컴포넌트 렌더링 (엑셀처럼 직접 수정 가능)
        with st.form("timetable_form"):
            edited_df = st.data_editor(
                df_timetable,
                column_config={
                    "요일": st.column_config.SelectboxColumn("요일", options=["월", "화", "수", "목", "금", "토"], required=True),
                    "과목명": st.column_config.TextColumn("수업명 (예: 인공지능개론)", required=True),
                    "시작시간": st.column_config.SelectboxColumn("시작", options=time_options, required=True),
                    "종료시간": st.column_config.SelectboxColumn("종료", options=time_options, required=True)
                },
                num_rows="dynamic",
                use_container_width=True,
                height=300
            )

            submitted_timetable = st.form_submit_button("시간표 저장 및 업데이트 🚀", use_container_width=True)

            if submitted_timetable:
                # 빈 값(NaN)이 들어간 행 제거 후 리스트 딕셔너리로 변환
                clean_df = edited_df.dropna(subset=["요일", "과목명", "시작시간", "종료시간"])
                new_timetable_list = clean_df.to_dict('records')

                # 프로필 업데이트 및 JSON 파일 저장
                profile["timetable"] = new_timetable_list
                save_profile(profile)
                
                # 세션 상태 최신화
                st.session_state.user_profile = profile
                
                st.success("🎉 정규 시간표가 성공적으로 저장되었습니다! 이제 비교과 추천 시 시간이 겹치면 경고해 드립니다.")
                st.rerun()

else:
    st.error("프로필 데이터를 파싱할 수 없습니다. 메인 화면에서 온보딩을 진행해 주세요.")