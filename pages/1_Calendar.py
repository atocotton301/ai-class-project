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
    st.session_state.my_schedule = st.session_state.user_profile.get('my_schedule', [])

import json
import os
def save_profile():
    st.session_state.user_profile['my_schedule'] = st.session_state.my_schedule
    path = f"data/{st.session_state.login_id}_profile.json"
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st.session_state.user_profile, f, ensure_ascii=False, indent=4)

user_profile = st.session_state.user_profile
user_name = user_profile.get("name", "학생")
st.write(f"**{user_name}**님, 원하는 분야만 쏙쏙 골라 일정을 확인하세요. (👇 **일정을 클릭해서 담아보세요!**)")
st.caption("💡 원활한 이용을 위해 최신 데이터는 1시간마다 최초 1회만 스크랩해옵니다. (접속/계정 변경 시 즉시 로딩)")
st.markdown("---")

# 2. 실데이터 크롤링 함수 (기존 더미데이터 구조와 호환되게)
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_calendar_data():
    import requests
    from bs4 import BeautifulSoup
    import re
    
    programs_dict = {
        "프로그램명": [],
        "분야": [],
        "카테고리": [],
        "시작일시": [],
        "종료일시": [],
        "포인트": [],
        "소요시간(시간)": [],
        "색상": []
    }
    
    colors = ["#FFB3B3", "#B3D9FF", "#B3E6CC", "#FFD9B3", "#D9B3FF"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        page = 1
        while page <= 10:  # 최대 10페이지까지만 탐색 (안전장치)
            url = f"https://hsportal.hansung.ac.kr/ko/program/all/list/all/1/{page}"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 실제 프로그램 아이템 목록 추출
            items = soup.select('div[data-module="eco"][data-role="item"]')
            
            # 더 이상 프로그램이 없으면(마지막 페이지를 넘어가면) 루프 종료
            if not items:
                break
                
            for item in items:
                title_elem = item.find(class_='title')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                inst_elem = item.find(class_='institution')
                institution = inst_elem.get_text(strip=True) if inst_elem else "일반"
                
                # 포인트 파싱 (D-Day 숫자와 혼동되지 않도록 <i class="point"> 요소 찾기)
                points = 0
                point_elem = item.find('i', class_='point')
                if point_elem and point_elem.next_sibling:
                    match = re.search(r'(\d+)', str(point_elem.next_sibling))
                    if match:
                        points = int(match.group(1))
                        
                # 일정(운영기간) 파싱
                date_layers = item.find_all(class_='date_layer')
                start_dt, end_dt = None, None
                for dl in date_layers:
                    if '운영:' in dl.get_text():
                        times = dl.find_all('time')
                        if len(times) >= 2:
                            start_dt = times[0].get('datetime')[:19]  # "2026-06-18T09:00:00"
                            end_dt = times[1].get('datetime')[:19]
                        elif len(times) == 1:
                            start_dt = end_dt = times[0].get('datetime')[:19]
                
                if not start_dt:
                    continue
                
                color = colors[len(programs_dict["프로그램명"]) % len(colors)]
                
                programs_dict["프로그램명"].append(title)
                programs_dict["분야"].append(institution.split()[0] if institution else "기타")
                programs_dict["카테고리"].append(institution)
                programs_dict["시작일시"].append(start_dt)
                programs_dict["종료일시"].append(end_dt)
                programs_dict["포인트"].append(points)
                programs_dict["소요시간(시간)"].append(2) # 임의의 소요시간
                programs_dict["색상"].append(color)
                
            page += 1
            
    except Exception as e:
        st.error(f"데이터를 불러오는데 실패했습니다: {e}")
        pass
        
    return programs_dict

with st.spinner("🚀 학교 서버에서 프로그램들을 가져오고 있어요! 🧚‍♀️✨"):
    mock_data = fetch_calendar_data()

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
                        "start": event_data['start'][:10], # 날짜만 잘라서 저장
                        "is_completed": False
                    })
                    save_profile()
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
                        save_profile()
                        st.rerun()
            
            st.markdown("---")
            st.metric("✨ 총 획득 예정 포인트", f"{total_points} pt")