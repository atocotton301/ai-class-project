import streamlit as st
import json
import os
from datetime import datetime, timedelta, time

# 세션 상태 초기화: 커스텀(분할) 일정 보관함 생성
if 'custom_schedules' not in st.session_state:
    st.session_state.custom_schedules = []

# =========================================================
# 📌 팝업 모듈: 장기 비교과 다중 요일 일괄 지정 및 개별 관리
# =========================================================
@st.dialog("⚙️ 상세 일정 관리")
def manage_custom_slots_popup(item_index):
    """
    메인 UI의 복잡도를 낮추기 위해, 부모 아이템(비교과) 하나에 종속된 
    여러 개의 하위 일정(조각)들을 팝업 내부에서 일괄 생성 및 삭제하도록 캡슐화함.
    """
    item = st.session_state.my_schedule[item_index]
    
    if 'custom_slots' not in item:
        item['custom_slots'] = []
        
    st.markdown(f"### ✨ {item['title']}")
    st.caption("담당자와 협의한 요일과 시간을 선택하여 한 번에 추가하세요.")
    
    with st.container(border=True):
        st.write("#### ➕ 일정 일괄 추가")
        selected_days = st.multiselect("📅 반복할 요일 선택", ["월", "화", "수", "목", "금"], default=[], placeholder="선택된 요일 없음 (클릭하여 추가)")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        hour_opts = [str(h).zfill(2) for h in range(9, 23)]
        min_opts = [str(m).zfill(2) for m in range(0, 60, 5)]
        
        with col1:
            start_h = st.selectbox("시", hour_opts, index=hour_opts.index("09"), key="b_sh")
        with col2:
            start_m = st.selectbox("분", min_opts, index=0, key="b_sm")
        with col3:
            new_dur = st.number_input("⏳ 진행(시간)", min_value=1, max_value=10, value=2)
            
        if st.button("선택한 요일 일괄 추가하기", type="primary", use_container_width=True):
            if not selected_days:
                st.error("최소 하나의 요일을 선택해 주세요!")
            else:
                base_date = datetime(2026, 6, 8) 
                day_map = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4}
                
                for d in selected_days:
                    target_date = base_date + timedelta(days=day_map[d])
                    target_time = time(int(start_h), int(start_m))
                    target_dt = datetime.combine(target_date, target_time)
                    
                    item['custom_slots'].append({
                        "title": item['title'],
                        "start": target_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                        "duration": new_dur,
                        "is_custom": True
                    })
                st.success("🎉 일괄 등록이 완료되었습니다!")
                st.rerun()

    st.markdown("#### 📋 등록된 세부 일정 목록")
    if not item['custom_slots']:
        st.info("아직 배정된 일정이 없습니다. 위에서 일정을 추가해 주세요.")
    else:
        for idx, slot in enumerate(item['custom_slots']):
            dt = datetime.fromisoformat(slot['start'])
            day_str = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
            
            c1, c2 = st.columns([8, 2])
            with c1:
                st.write(f"🔹 **{dt.date()} ({day_str})** {dt.strftime('%H:%M')} ~ ({slot['duration']}시간)")
            with c2:
                if st.button("❌", key=f"del_slot_{item_index}_{idx}"):
                    item['custom_slots'].pop(idx)
                    st.rerun()

# =========================================================
# 충돌 감지(Collision Detection) 코어 알고리즘
# =========================================================
def check_collisions(regular_classes, extra_slots):
    """
    정규 수업과 오버레이될 비교과 프로그램 간의 분(Minute) 단위 교집합을 검사함.
    """
    warnings = []
    days_arr = ["월", "화", "수", "목", "금"]
    
    for e_slot in extra_slots:
        e_dt = datetime.fromisoformat(e_slot['start'])
        if e_dt.weekday() >= 5: continue
        e_day = days_arr[e_dt.weekday()]
        
        e_start_mins = e_dt.hour * 60 + e_dt.minute
        e_end_mins = e_start_mins + int(float(e_slot['duration'])) * 60
        
        for r_cls in regular_classes:
            if r_cls['요일'] == e_day:
                r_sh, r_sm = map(int, r_cls['시작시간'].split(':'))
                r_eh, r_em = map(int, r_cls['종료시간'].split(':'))
                r_start_mins = r_sh * 60 + r_sm
                r_end_mins = r_eh * 60 + r_em
                
                if max(e_start_mins, r_start_mins) < min(e_end_mins, r_end_mins):
                    warnings.append(f"🚨 **[{e_day}] {e_slot['title']}** 일정이 **{r_cls['과목명']}** 수업과 겹칩니다!")
                    
    return list(set(warnings)) 

# =========================================================
# 메인 대시보드 로직 시작
# =========================================================
st.title("🚀 나의 대시보드")
st.write("나의 성취도와 이번 주 융합 시간표를 한눈에 확인하세요!")

def load_profile():
    if 'login_id' not in st.session_state:
        return {}
    path = f"data/{st.session_state.login_id}_profile.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

profile = load_profile()

if not profile:
    st.warning("⚠️ 메인 화면에서 온보딩을 먼저 완료해 주세요.")
    st.stop()

if 'my_schedule' not in st.session_state:
    st.session_state.my_schedule = profile.get('my_schedule', [])
my_schedule = st.session_state.my_schedule
current_timetable = profile.get("timetable", [])

def save_profile():
    profile['my_schedule'] = st.session_state.my_schedule
    st.session_state.user_profile = profile
    path = f"data/{st.session_state.login_id}_profile.json"
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)

# =========================================================
# 🔔 1. 스마트 푸시 알림 시스템 (백그라운드 처리 및 Toast 팝업)
# =========================================================
# 시연을 위해 가상의 현재 날짜를 2026년 6월 6일로 고정
SIMULATED_TODAY = datetime(2026, 6, 6) 

# 대시보드 진입 시 브라우저 하단에만 가볍게 푸시 알림(Toast) 제공
for ex in my_schedule:
    target_dt = datetime.fromisoformat(ex['start'])
    d_day = (target_dt.date() - SIMULATED_TODAY.date()).days
    
    if 0 <= d_day <= 3:
        d_text = "오늘" if d_day == 0 else f"{d_day}일"
        st.toast(f"마감 임박: '{ex['title']}' 프로그램이 {d_text} 남았습니다!", icon="🚨")

# =========================================================
# 2. 🏆 포인트 시뮬레이터
# =========================================================
st.markdown("### 🏆 이번 학기 목표 달성 시뮬레이터")

curr_pts = int(profile.get('current_points', 0))
target_pts = int(profile.get('target_points', 150)) 

# 실제 취득 포인트 기반 계산
raw_actual_extra = sum(int(ex.get('points', 0)) for ex in my_schedule if ex.get('is_completed', False))
actual_recognized_pts = min(raw_actual_extra, 200)
actual_carryover_pts = min(max(raw_actual_extra - 200, 0), 200)
actual_expired_pts = max(raw_actual_extra - 400, 0)
actual_total_pts = curr_pts + actual_recognized_pts

# 예상 포인트 기반 계산
raw_expected_extra = sum(int(ex.get('points', 0)) for ex in my_schedule)
expected_recognized_pts = min(raw_expected_extra, 200)
expected_total_pts = curr_pts + expected_recognized_pts

col1, col2, col3, col4 = st.columns(4)
col1.metric("시작 포인트", f"{curr_pts} pt", help="이전 학기까지 누적된 포인트입니다.")
col2.metric("이번 학기 인정 포인트", f"{actual_recognized_pts} pt", delta=f"실제 취득: {raw_actual_extra} pt", delta_color="off", help="이번 학기에 취득한 포인트 중 최대 200pt까지만 인정됩니다.")

if actual_expired_pts > 0:
    col3.metric("다음 학기 이월 포인트", f"{actual_carryover_pts} pt", delta=f"⚠️ {actual_expired_pts}pt 초과 소멸", delta_color="inverse", help="200pt를 초과한 부분은 최대 200pt까지 다음 학기로 이월됩니다.")
else:
    col3.metric("다음 학기 이월 포인트", f"{actual_carryover_pts} pt", delta=f"예상 이월: {min(max(raw_expected_extra - 200, 0), 200)} pt", delta_color="normal", help="200pt를 초과한 부분은 최대 200pt까지 다음 학기로 이월됩니다.")

col4.metric("졸업인정 누적 포인트", f"{actual_total_pts} pt", help="시작 포인트와 이번 학기 인정 포인트를 합산한 최종 누적 포인트입니다.")

st.progress(min(actual_total_pts / target_pts if target_pts else 0, 1.0), text="현재 실제 목표 달성도")
st.progress(min(expected_total_pts / target_pts if target_pts else 0, 1.0), text="즐겨찾기 100% 완료 시 예상 목표 달성도")
st.markdown("---")

# =========================================================
# 3. 📚 통합 즐겨찾기 보관함 (마감 임박 UI 인라인 통합)
# =========================================================
st.markdown("### 📚 나의 비교과 보관함 & 일정 관리")

if my_schedule:
    for i, ex in enumerate(my_schedule):
        duration = float(ex.get('duration', 0))
        is_flexible = duration >= 10 
        
        # 🚨 D-Day 계산 로직 추가
        target_dt = datetime.fromisoformat(ex['start'])
        d_day = (target_dt.date() - SIMULATED_TODAY.date()).days

        with st.container(border=True):
            c_info, c_action1, c_action2 = st.columns([6, 2, 2])
            
            with c_info:
                # 🚨 수정된 부분: 거추장스러운 배너 대신, 아이템 제목 옆에 예쁜 경고 텍스트/이모지 삽입
                if 0 <= d_day <= 3:
                    d_badge = "D-Day" if d_day == 0 else f"D-{d_day}"
                    st.markdown(f"**✨ {ex['title']}** <span style='color: #d32f2f; font-weight: bold; font-size: 0.85em; margin-left: 8px;'>🚨 마감 {d_badge}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**✨ {ex['title']}**")
                    
                slots_count = len(ex.get('custom_slots', []))
                status_text = f" | 🗓️ 분할 일정 {slots_count}개 배정됨" if slots_count > 0 else ""
                st.caption(f"⏱️ 총 {ex.get('duration', 0)}시간 | 🏆 {ex.get('points', 0)}pt {status_text}")
                
            with c_action1:
                if is_flexible:
                    if st.button("⚙️ 일정 관리", key=f"mng_{i}", use_container_width=True):
                        manage_custom_slots_popup(i)
                else:
                    st.markdown("<div style='text-align: center; color: #2E7D32; font-size: 0.9em; padding-top: 10px;'>✅ 시간표 고정됨</div>", unsafe_allow_html=True)
            
            with c_action2:
                if not ex.get('is_completed', False):
                    if st.button("✅ 취득완료", key=f"comp_{i}", use_container_width=True):
                        ex['is_completed'] = True
                        save_profile()
                        st.rerun()
                else:
                    st.markdown("<div style='text-align: center; color: #1565C0; font-size: 0.9em; padding-top: 10px; font-weight: bold;'>🎉 취득 완료됨</div>", unsafe_allow_html=True)
                    
                if st.button("❌ 빼기", key=f"del_{i}", use_container_width=True):
                    st.session_state.my_schedule.pop(i)
                    save_profile()
                    st.rerun()
else:
    st.info("보관함이 비어 있습니다. 캘린더에서 관심 있는 프로그램을 즐겨찾기 해보세요!")

st.write("")

# =========================================================
# 4. 데이터 취합 및 스마트 충돌 감지
# =========================================================
all_display_slots = []
for ex in my_schedule:
    if float(ex.get('duration', 0)) < 10:
        all_display_slots.append(ex)
    else:
        all_display_slots.extend(ex.get('custom_slots', []))

st.markdown("### ⏰ 정규 수업 & 융합 시간표")

show_extra = st.toggle("✨ 시간표 내 비교과 겹쳐 보기", value=True)

if show_extra:
    collision_warnings = check_collisions(current_timetable, all_display_slots)
    if collision_warnings:
        with st.container(border=True):
            st.error("⚠️ **주의: 정규 수업과 겹치는 비교과 일정이 있습니다!**")
            for w in collision_warnings:
                st.write(w)

# =========================================================
# 5. 융합 시간표 렌더링
# =========================================================
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
    box-shadow: 0 2px 4px rgba(0,0,0,0.15); overflow: hidden; z-index: 10;
    display: flex; flex-direction: column; justify-content: center;
}
.class-title { margin-bottom: 2px; font-size: 12px;}
.class-time { font-size: 10px; font-weight: normal; opacity: 0.8;}
</style>
""", unsafe_allow_html=True)

color_palette = [
    {"bg": "#E8F0FE", "border": "#64B5F6", "text": "#1565C0"}, 
    {"bg": "#E8F5E9", "border": "#81C784", "text": "#2E7D32"}, 
    {"bg": "#FFF3E0", "border": "#FFB74D", "text": "#E65100"}, 
    {"bg": "#F3E5F5", "border": "#BA68C8", "text": "#6A1B9A"}, 
]

unique_classes = list(set([c['과목명'] for c in current_timetable]))
color_map = {name: color_palette[i % len(color_palette)] for i, name in enumerate(unique_classes)}
extra_color = {"bg": "#E1BEE7", "border": "#8E24AA", "text": "#4A148C"}

days = ["월", "화", "수", "목", "금"]
hours = range(9, 23) 

html = "<div class='timetable-wrapper'>"
html += "<div class='time-col'><div class='tt-header'></div>" 
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
        
        top_px = ((sh - 9) * 60) + sm
        height_px = ((eh - 9) * 60 + em) - top_px
        c_color = color_map[c['과목명']]
        
        html += f"<div class='class-block' style='top: {top_px}px; height: {height_px}px; background-color: {c_color['bg']}; color: {c_color['text']}; border-left: 3px solid {c_color['border']};'>"
        html += f"<div class='class-title'>{c['과목명']}</div>"
        html += f"<div class='class-time'>{c['시작시간']}~{c['종료시간']}</div>"
        html += "</div>"

    if show_extra and all_display_slots:
        for ex in all_display_slots:
            dt = datetime.fromisoformat(ex['start'])
            
            if dt.weekday() < 5 and days[dt.weekday()] == day:
                sh, sm = dt.hour, dt.minute
                duration_hours = int(float(ex.get('duration', 2))) 
                
                top_px = ((sh - 9) * 60) + sm
                height_px = min(duration_hours * 60, (23 - 9) * 60 - top_px) 
                
                pts_text = "🧩 조각 일정" if ex.get('is_custom') else f"{ex.get('points', 0)}pt"
                
                html += f"<div class='class-block' style='top: {top_px}px; height: {height_px}px; background-color: {extra_color['bg']}; color: {extra_color['text']}; border-left: 5px solid {extra_color['border']}; z-index: 20; box-shadow: 0 6px 12px rgba(142, 36, 170, 0.4); opacity: 0.95;'>"
                html += f"<div class='class-title'>✨ {ex['title']}</div>"
                html += f"<div class='class-time'>{sh:02d}:{sm:02d} (+{duration_hours}H) | {pts_text}</div>"
                html += "</div>"
                
    html += "</div></div>"
html += "</div>"

st.markdown(html, unsafe_allow_html=True)