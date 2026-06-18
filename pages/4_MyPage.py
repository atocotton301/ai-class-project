import streamlit as st
import pandas as pd
import json
import os

# =========================================================
# 📌 팝업창(모달) 함수 정의 
# =========================================================
@st.dialog("➕ 새 수업 추가")
def add_class_popup(profile):
    st.markdown("추가할 과목과 시간을 선택해 주세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        new_day = st.selectbox("요일", ["월", "화", "수", "목", "금"])
        new_name = st.text_input("과목명 (필수)", placeholder="예) 경제학입문")
        
    with col2:
        hour_opts = [str(h).zfill(2) for h in range(9, 23)]
        min_opts = [str(m).zfill(2) for m in range(0, 60, 5)]
        
        st.write("⏱️ 시작 시간")
        c_sh, c_sm = st.columns(2)
        with c_sh:
            start_h = st.selectbox("시", hour_opts, key="add_sh", label_visibility="collapsed")
        with c_sm:
            start_m = st.selectbox("분", min_opts, key="add_sm", label_visibility="collapsed")
            
        st.write("🏁 종료 시간")
        c_eh, c_em = st.columns(2)
        with c_eh:
            end_h = st.selectbox("시", hour_opts, index=1, key="add_eh", label_visibility="collapsed")
        with c_em:
            end_m = st.selectbox("분", min_opts, index=6, key="add_em", label_visibility="collapsed")
            
    new_start = f"{start_h}:{start_m}"
    new_end = f"{end_h}:{end_m}"
        
    if st.button("저장하기", type="primary", use_container_width=True):
        if not new_name.strip():
            st.error("과목명을 입력해 주세요!")
        elif new_start >= new_end:
            st.error("종료 시간이 시작 시간보다 빠르거나 같을 수 없습니다!")
        else:
            new_class = {
                "요일": new_day,
                "과목명": new_name.strip(),
                "시작시간": new_start,
                "종료시간": new_end
            }
            current_timetable = profile.get("timetable", [])
            current_timetable.append(new_class)
            profile["timetable"] = current_timetable
            
            os.makedirs("data", exist_ok=True)
            with open(f"data/{st.session_state.login_id}_profile.json", "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            st.session_state.user_profile = profile
            
            st.success("수업이 추가되었습니다!")
            st.rerun()

@st.dialog("✏️ 수업 정보 수정")
def edit_class_popup(profile, idx, current_data):
    st.markdown("수정할 내용을 입력해 주세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        days = ["월", "화", "수", "목", "금"]
        default_day_idx = days.index(current_data["요일"]) if current_data["요일"] in days else 0
        new_day = st.selectbox("요일", days, index=default_day_idx)
        
        new_name = st.text_input("과목명 (필수)", value=current_data["과목명"])
        
    with col2:
        hour_opts = [str(h).zfill(2) for h in range(9, 23)]
        min_opts = [str(m).zfill(2) for m in range(0, 60, 5)]
        
        curr_sh, curr_sm = current_data["시작시간"].split(":")
        curr_eh, curr_em = current_data["종료시간"].split(":")
        
        st.write("⏱️ 시작 시간")
        c_sh, c_sm = st.columns(2)
        with c_sh:
            start_h = st.selectbox("시", hour_opts, index=hour_opts.index(curr_sh), key="edit_sh", label_visibility="collapsed")
        with c_sm:
            start_m = st.selectbox("분", min_opts, index=min_opts.index(curr_sm), key="edit_sm", label_visibility="collapsed")
            
        st.write("🏁 종료 시간")
        c_eh, c_em = st.columns(2)
        with c_eh:
            end_h = st.selectbox("시", hour_opts, index=hour_opts.index(curr_eh), key="edit_eh", label_visibility="collapsed")
        with c_em:
            end_m = st.selectbox("분", min_opts, index=min_opts.index(curr_em), key="edit_em", label_visibility="collapsed")

    new_start = f"{start_h}:{start_m}"
    new_end = f"{end_h}:{end_m}"
        
    if st.button("수정 완료", type="primary", use_container_width=True):
        if not new_name.strip():
            st.error("과목명을 입력해 주세요!")
        elif new_start >= new_end:
            st.error("종료 시간이 시작 시간보다 빠르거나 같을 수 없습니다!")
        else:
            profile["timetable"][idx] = {
                "요일": new_day,
                "과목명": new_name.strip(),
                "시작시간": new_start,
                "종료시간": new_end
            }
            os.makedirs("data", exist_ok=True)
            with open(f"data/{st.session_state.login_id}_profile.json", "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            st.session_state.user_profile = profile
            
            st.success("수업이 수정되었습니다!")
            st.rerun()

@st.dialog("🔄 학기 마감 및 포인트 갱신")
def end_term_dialog(profile):
    st.markdown("현재 학기를 마감하고 획득한 포인트를 다음 학기로 이월하시겠습니까?")
    st.info("보관함(즐겨찾기 및 취득완료 내역)이 초기화되며, 실제 취득한 포인트가 누적 시작 포인트로 갱신됩니다.")
    if st.button("확인 및 이월하기", type="primary", use_container_width=True):
        curr_pts = int(profile.get('current_points', 0))
        my_schedule = profile.get('my_schedule', [])
        raw_actual_extra = sum(int(ex.get('points', 0)) for ex in my_schedule if ex.get('is_completed', False))
        
        actual_recognized_pts = min(raw_actual_extra, 200)
        actual_carryover_pts = min(max(raw_actual_extra - 200, 0), 200)
        
        # 누적 시작 포인트 갱신
        profile['current_points'] = curr_pts + actual_recognized_pts
        
        # 다음 학기를 위해 보관함 초기화 및 이월 포인트 부여
        if actual_carryover_pts > 0:
            profile['my_schedule'] = [{
                "title": "지난 학기 이월 포인트",
                "points": actual_carryover_pts,
                "is_completed": True,
                "duration": 0,
                "category": "시스템 자동 이월",
                "start": "학기 시작"
            }]
        else:
            profile['my_schedule'] = []
        
        with open(f"data/{st.session_state.login_id}_profile.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)
            
        st.session_state.user_profile = profile
        st.session_state.my_schedule = []
        st.success("새 학기 포인트로 갱신되었습니다!")
        st.rerun()

@st.dialog("🚨 회원 탈퇴")
def delete_account_dialog(profile):
    st.markdown("정말 탈퇴하시겠습니까?")
    st.error("탈퇴 시 계정 정보, 프로필, 비교과 보관함, 포인트 기록이 **모두 삭제**됩니다. (단, 익명 리뷰는 유지됩니다)")
    if st.button("최종 확인 (탈퇴하기)", type="primary", use_container_width=True):
        login_id = st.session_state.login_id
        
        users_db_path = "data/users_db.json"
        if os.path.exists(users_db_path):
            with open(users_db_path, "r", encoding="utf-8") as f:
                users = json.load(f)
            if login_id in users:
                del users[login_id]
                with open(users_db_path, "w", encoding="utf-8") as f:
                    json.dump(users, f, ensure_ascii=False, indent=4)
                    
        profile_path = f"data/{login_id}_profile.json"
        if os.path.exists(profile_path):
            os.remove(profile_path)
            
        st.session_state.clear()
        st.rerun()

# =========================================================
# 메인 페이지 로직 시작
# =========================================================
st.title("👤 마이페이지")

if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면에서 온보딩을 먼저 완료해 주세요.")
    st.stop()

DATA_PATH = f"data/{st.session_state.login_id}_profile.json"

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
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    st.subheader(f"**{profile.get('name')}** 님의 개인 공간")
    tab_profile, tab_timetable = st.tabs(["👤 기본 프로필 관리", "📅 정규 시간표 관리"])

    # ---------------------------------------------------------
    # [TAB 1] 프로필 조회 및 수정 모드
    # ---------------------------------------------------------
    with tab_profile:
        if not st.session_state.edit_mode:
            # ✨ 프로필 이미지 요소를 완전히 지우고 텍스트 정보만 정렬되게 컨테이너를 비웠습니다.
            with st.container(border=True):
                st.write(f"**👤 이름:** {profile.get('name')}")
                st.write(f"**🆔 학번:** {profile.get('student_id')}")
                st.write(f"**🎓 전공:** {profile.get('major')}")
                st.write(f"**📧 이메일:** {profile.get('email')}")

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
                
            st.markdown("---")
            st.write("### ⚙️ 계정 및 학기 관리")
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button("🔄 학기 마감 (포인트 이월)", use_container_width=True):
                    end_term_dialog(profile)
            with col_action2:
                if st.button("🚨 회원 탈퇴", use_container_width=True):
                    delete_account_dialog(profile)
                
        else:
            st.markdown("### 📝 프로필 수정하기")
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
                            "timetable": profile.get('timetable', [])  
                        }
                        
                        save_profile(updated_profile)
                        st.session_state.user_profile = updated_profile
                        st.session_state.edit_mode = False
                        st.success("프로필 수정이 완료되었습니다.")
                        st.rerun()
                        
                if cancel_submitted:
                    st.session_state.edit_mode = False
                    st.rerun()

    # ---------------------------------------------------------
    # [TAB 2] 정규 시간표 입력 및 수정 
    # ---------------------------------------------------------
    with tab_timetable:
        st.markdown("### 🏫 나의 정규 수업 시간표")
        st.caption("비교과 프로그램 신청 시 **수업 시간 겹침 경고 알림**을 받기 위해 정확히 입력해 주세요.")
        
        current_timetable = profile.get("timetable", [])

        if st.button("➕ 새 수업 추가하기", type="primary", use_container_width=True):
            add_class_popup(profile)
            
        with st.expander("🛠️ 등록된 수업 관리 (수정 및 삭제)", expanded=bool(current_timetable)):
            if current_timetable:
                for idx, c in enumerate(current_timetable):
                    with st.container(border=True):
                        col_c1, col_c2, col_c3 = st.columns([5, 1.5, 1.5])
                        with col_c1:
                            st.write(f"📘 **{c['과목명']}** | {c['요일']} {c['시작시간']} ~ {c['종료시간']}")
                        with col_c2:
                            if st.button("✏️ 수정", key=f"edit_{idx}", use_container_width=True):
                                edit_class_popup(profile, idx, c)
                        with col_c3:
                            if st.button("🗑️ 삭제", key=f"del_{idx}", use_container_width=True):
                                current_timetable.pop(idx)
                                profile["timetable"] = current_timetable
                                save_profile(profile)
                                st.session_state.user_profile = profile
                                st.rerun()
            else:
                st.info("현재 등록된 수업이 없습니다. 위의 버튼을 눌러 추가해 주세요.")

        st.markdown("---")

        st.markdown("""
        <style>
        .timetable-wrapper { display: flex; width: 100%; border-top: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; font-family: sans-serif; background: white;}
        .time-col { width: 12%; border-right: 1px solid #e0e0e0; background-color: #f9f9f9; }
        .day-col { flex: 1; border-right: 1px solid #e0e0e0; position: relative; }
        .day-col:last-child { border-right: none; }
        .tt-header { height: 40px; line-height: 40px; text-align: center; font-weight: bold; border-bottom: 1px solid #e0e0e0; background-color: #f9f9f9; color: #555; font-size: 13px;}
        .time-slot { height: 60px; border-bottom: 1px solid #eee; text-align: center; color: #888; font-size: 11px; box-sizing: border-box; padding-top: 5px;}
        .time-slot-empty { height: 60px; border-bottom: 1px solid #eee; box-sizing: border-box; }
        
        .class-block {
            position: absolute; left: 2px; right: 2px;
            border-radius: 4px; padding: 6px; font-size: 11px; font-weight: bold;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; z-index: 10;
            display: flex; flex-direction: column; justify-content: center;
        }
        .class-title { margin-bottom: 2px; font-size: 12px;}
        .class-time { font-size: 10px; font-weight: normal; opacity: 0.8;}
        </style>
        """, unsafe_allow_html=True)
        
        color_palette = [
            {"bg": "#FFEBEE", "border": "#E57373", "text": "#C62828"}, 
            {"bg": "#E8F0FE", "border": "#64B5F6", "text": "#1565C0"}, 
            {"bg": "#E8F5E9", "border": "#81C784", "text": "#2E7D32"}, 
            {"bg": "#FFF3E0", "border": "#FFB74D", "text": "#E65100"}, 
            {"bg": "#F3E5F5", "border": "#BA68C8", "text": "#6A1B9A"}, 
            {"bg": "#E0F7FA", "border": "#4DD0E1", "text": "#00838F"}, 
            {"bg": "#FFF9C4", "border": "#FFD54F", "text": "#F57F17"}, 
        ]
        
        unique_classes = []
        for c in current_timetable:
            if c['과목명'] not in unique_classes:
                unique_classes.append(c['과목명'])
                
        color_map = {name: color_palette[i % len(color_palette)] for i, name in enumerate(unique_classes)}

        days = ["월", "화", "수", "목", "금"]
        hours = range(9, 23) 
        
        html = "<div class='timetable-wrapper'>"
        
        html += "<div class='time-col'>"
        html += "<div class='tt-header'></div>" 
        for h in hours:
            time_label = f"오전 {h}시" if h < 12 else (f"오후 {h-12}시" if h > 12 else "오후 12시")
            html += f"<div class='time-slot'>{time_label}</div>"
        html += "</div>"
        
        for day in days:
            html += "<div class='day-col'>"
            html += f"<div class='tt-header'>{day}</div>"
            
            html += "<div style='position: relative; width: 100%;'>"
            for h in hours:
                html += "<div class='time-slot-empty'></div>"
                
            day_classes = [c for c in current_timetable if c['요일'] == day]
            for c in day_classes:
                sh, sm = map(int, c['시작시간'].split(':'))
                eh, em = map(int, c['종료시간'].split(':'))
                
                start_mins = (sh - 9) * 60 + sm
                end_mins = (eh - 9) * 60 + em
                duration_mins = end_mins - start_mins
                
                top_px = start_mins
                height_px = duration_mins
                
                c_color = color_map[c['과목명']]
                
                html += f"<div class='class-block' style='top: {top_px}px; height: {height_px}px; background-color: {c_color['bg']}; color: {c_color['text']}; border-left: 3px solid {c_color['border']};'>"
                html += f"<div class='class-title'>{c['과목명']}</div>"
                html += f"<div class='class-time'>{c['시작시간']}~{c['종료시간']}</div>"
                html += "</div>"
                
            html += "</div></div>"
            
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

else:
    st.error("프로필 데이터를 파싱할 수 없습니다. 메인 화면에서 온보딩을 진행해 주세요.")