import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

# 🖥️ 화면을 좌우로 넓게 쓰기 위한 필수 설정
st.set_page_config(layout="wide")
st.title("📅 한스플랜 맞춤형 캘린더")

# 1. 로그인 상태 확인
if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면(온보딩)에서 먼저 프로필을 설정해 주세요!")
    st.stop()

# 보관함(즐겨찾기) 세션 초기화
if 'my_schedule' not in st.session_state:
    st.session_state.my_schedule = []

user_profile = st.session_state.user_profile
user_name = user_profile.get("name", "학생")
st.write(f"**{user_name}**님, 원하는 분야만 쏙쏙 골라 일정을 확인하세요. (👇 **일정을 클릭해서 담아보세요!**)")
st.markdown("---")

# 2. 더미 데이터 세팅
mock_data = {
    "프로그램명": [
        "파이썬 기초 특강", "도서관 근로 장학생", "AI 해커톤", "글로벌 멘토링", "취업 면접 컨설팅", 
        "상상부기 피어코칭", "인공지능 트렌드 세미나", "기초 코딩 역량 강화"
    ],
    "분야": ["창의융합", "사회봉사", "창의융합", "글로벌", "취업/창업", "학습법", "창의융합", "학습법"],
    "카테고리": [
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "사회봉사 및 인성 함양 (교내외 봉사활동, 멘토링 프로그램)", 
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "글로벌역량 프로그램 (어학, 교환학생, 다문화 이해 등)",
        "취·창업 지원 프로그램 (포트폴리오, 면접 컨설팅, 창업 동아리)",
        "학습인프라/학습법 강화 (학습 튜터링, 상상부기 피어코칭)",
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)",
        "학습인프라/학습법 강화 (학습 튜터링, 상상부기 피어코칭)"
    ],
    "시작일시": ["2026-06-08T14:00:00", "2026-06-09T09:00:00", "2026-06-12T10:00:00", "2026-06-16T18:00:00", "2026-06-18T15:00:00", "2026-06-19T13:00:00", "2026-06-09T13:00:00", "2026-06-09T15:00:00"],
    "종료일시": ["2026-06-08T16:00:00", "2026-06-09T12:00:00", "2026-06-13T18:00:00", "2026-06-16T20:00:00", "2026-06-18T17:00:00", "2026-06-19T15:00:00", "2026-06-09T15:00:00", "2026-06-09T17:00:00"],
    "포인트": [30, 100, 200, 150, 50, 80, 40, 60],
    "소요시간(시간)": [10, 50, 48, 30, 5, 20, 4, 12],
    "색상": ["#FFB3B3", "#B3D9FF", "#FFB3B3", "#B3E6CC", "#FFD9B3", "#D9B3FF", "#FFB3B3", "#D9B3FF"] 
}
df = pd.DataFrame(mock_data)

# 3. 🖥️ 화면 7:3 비율 분할 (왼쪽: 달력 영역, 오른쪽: 보관함 영역)
col_cal, col_book = st.columns([7, 3])

# ==========================================
# ⬅️ 왼쪽 영역: 캘린더 및 필터링
# ==========================================
with col_cal:
    st.markdown("### 🔍 카테고리 필터링")
    filter_options = ["전체보기"] + list(df['분야'].unique())
    selected_filter = st.pills("원하는 분야를 선택하세요", filter_options, default="전체보기", key="cal_filter")

    if selected_filter != "전체보기":
        filtered_df = df[df['분야'] == selected_filter]
    else:
        filtered_df = df.copy()

    # 달력 이벤트 구성
    calendar_events = []
    for _, row in filtered_df.iterrows():
        calendar_events.append({
            "title": row['프로그램명'],
            "start": row['시작일시'],
            "end": row['종료일시'],
            "backgroundColor": row['색상'],
            "borderColor": row['색상'],
            "textColor": "#000000",
            "extendedProps": {
                "category": row['카테고리'],
                "points": row['포인트'],
                "duration": row['소요시간(시간)']
            }
        })

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "initialDate": "2026-06-01",
        "initialView": "dayGridMonth",
        "displayEventTime": False,
        "height": 780, 
        "dayMaxEvents": 2, 
    }

    custom_css="""
        .fc { background-color: white; color: #333333; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .fc-toolbar-title { color: #1f1f1f !important; font-weight: 700; }
        .fc-button { background-color: #f0f2f6 !important; color: #1f1f1f !important; border: none !important; font-weight: 600 !important; }
        .fc-event { cursor: pointer; transition: transform 0.15s ease; }
        .fc-event:hover { transform: scale(1.02); z-index: 999 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .fc-event-title { white-space: normal !important; overflow: visible !important; font-weight: 600; font-size: 0.85em; line-height: 1.2; padding: 2px; }
        .fc-daygrid-more-link { color: #FF4B4B !important; font-weight: bold; font-size: 0.85em; padding-left: 4px; }
        .fc-popover { background-color: white !important; border-radius: 8px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; border: 1px solid #e0e0e0 !important; }
        .fc-popover-header { background-color: #f8f9fa !important; color: #1f1f1f !important; font-weight: bold !important; }
        .fc-popover-body { background-color: white !important; }
        .fc-popover .fc-event-title { color: #1f1f1f !important; }
    """

    # 캘린더 렌더링
    cal_result = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)

    # 클릭 이벤트 감지 및 상세 정보
    if cal_result.get("eventClick"):
        event_data = cal_result["eventClick"]["event"]
        props = event_data["extendedProps"]
        
        st.markdown("### 📋 선택한 프로그램 상세 정보")
        with st.container(border=True):
            st.subheader(f"✨ {event_data['title']}")
            st.write(f"**상세 분야:** {props['category']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🏆 지급 포인트", f"{props['points']} pt")
            c2.metric("⏱️ 소요 시간", f"{props['duration']} 시간")
            c3.metric("📅 시작일", event_data['start'][:10]) 
            
            st.markdown(" ")
            
            # 🎯 내 시간표에 담기 로직
            if st.button("⭐ 내 시간표에 담기 (즐겨찾기)", use_container_width=True):
                selected_title = event_data['title']
                already_saved = any(item['title'] == selected_title for item in st.session_state.my_schedule)
                
                if already_saved:
                    st.warning("이미 시간표에 담겨있는 프로그램입니다! 😅")
                else:
                    st.session_state.my_schedule.append({
                        "title": selected_title,
                        "category": props['category'],
                        "points": props['points'],
                        "duration": props['duration'],
                        "start": event_data['start'][:10] # 날짜만 잘라서 저장
                    })
                    st.success(f"🎉 담기 완료!")
                    st.rerun() # 추가 후 즉시 화면을 새로고침하여 우측 탭에 반영

# ==========================================
# ➡️ 오른쪽 영역: 내 시간표(즐겨찾기) 탭
# ==========================================
with col_book:
    st.markdown("### ⭐ My 시간표 보관함")
    
    with st.container(border=True):
        if not st.session_state.my_schedule:
            st.info("아직 담아둔 일정이 없습니다.\n달력에서 일정을 클릭해 담아보세요!")
        else:
            total_points = 0
            
            # 보관함 리스트 렌더링
            for idx, item in enumerate(st.session_state.my_schedule):
                total_points += item['points']
                with st.expander(f"📌 {item['title']}", expanded=True):
                    st.write(f"📅 **일정:** {item['start']}")
                    st.write(f"🏆 **포인트:** {item['points']} pt")
                    
                    # 삭제 버튼
                    if st.button("❌ 빼기", key=f"del_{idx}", use_container_width=True):
                        st.session_state.my_schedule.pop(idx)
                        st.rerun()
            
            st.markdown("---")
            st.metric("✨ 총 획득 예정 포인트", f"{total_points} pt")