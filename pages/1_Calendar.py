import streamlit as st
import pandas as pd
from utils.recommender import get_sorted_programs

st.title("📅 한스플랜 맞춤형 캘린더")

# 1. 로그인 상태 확인
if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면(온보딩)에서 먼저 프로필을 설정해 주세요!")
    st.stop()

# 유저 프로필 정보 연동
user_profile = st.session_state.user_profile
user_name = user_profile.get("name", "학생")
user_categories = user_profile.get("categories", [])

st.write(f"**{user_name}**님을 위한 이번 주 비교과 프로그램입니다.")

# 2. 더미 데이터 세팅 
mock_data = {
    "프로그램명": ["파이썬 기초 특강", "도서관 근로 장학생", "AI 해커톤", "글로벌 멘토링", "취업 면접 컨설팅", "상상부기 피어코칭"],
    "분야": ["창의융합", "사회봉사", "창의융합", "글로벌", "취업/창업", "학습법"], # 필터링을 위해 짧은 분야명 추가
    "카테고리": [
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "사회봉사 및 인성 함양 (교내외 봉사활동, 멘토링 프로그램)", 
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "글로벌역량 프로그램 (어학, 교환학생, 다문화 이해 등)",
        "취·창업 지원 프로그램 (포트폴리오, 면접 컨설팅, 창업 동아리)",
        "학습인프라/학습법 강화 (학습 튜터링, 상상부기 피어코칭)"
    ],
    "포인트": [30, 100, 200, 150, 50, 80],
    "일정": ["5.25(목) 14:00", "5.26(금) 09:00", "5.29(월) 10:00", "5.30(화) 18:00", "6.01(목) 15:00", "6.02(금) 13:00"],
    "소요시간(시간)": [10, 50, 48, 30, 5, 20],
    "꿀지수": [4.5, 3.0, 2.0, 4.0, 3.5, 4.5],
    "혜자지수": [4.0, 3.5, 5.0, 4.5, 4.0, 4.0]
}
df = pd.DataFrame(mock_data)

# 3. 🎯 동적 필터링 버튼 (분야별)
st.markdown("### 🔍 카테고리 필터링")
# '전체보기'를 포함하여 데이터에 있는 고유한 분야 리스트 생성
filter_options = ["전체보기"] + list(df['분야'].unique())
selected_filter = st.radio("원하는 분야를 선택하세요", filter_options, horizontal=True, label_visibility="collapsed")

# 4. 필터링 및 정렬 로직 적용
if selected_filter != "전체보기":
    df = df[df['분야'] == selected_filter]

# 기존에 만들었던 정렬 로직 (utils/recommender.py 연동)
sort_option = st.selectbox(
    "정렬 기준", 
    ["🔥 포인트 높은 순", "⏱️ 시간 대비 가성비 순", "🍯 꿀지수 (난이도) 높은 순", "💖 혜자지수 (만족도) 높은 순"]
)
sorted_df = get_sorted_programs(df, user_categories, sort_option)

st.markdown("---")
st.markdown("### 📌 일정 슬롯 (Focus Mode)")

if len(sorted_df) == 0:
    st.info("조건에 맞는 프로그램이 없습니다.")
else:
    # 5. 🎯 시각적 최적화 슬롯(Slot) 레이아웃 렌더링
    for index, row in sorted_df.iterrows():
        # 테두리가 있는 카드(슬롯) 형태로 컨테이너 생성
        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 2, 2])
            
            with col1:
                st.subheader(row['프로그램명'])
                st.caption(f"{row['카테고리']}")
            
            with col2:
                st.write(f"📅 **{row['일정']}**")
                st.write(f"⏱️ {row['소요시간(시간)']}시간 소요")
                
            with col3:
                st.markdown(f"#### 🏆 {row['포인트']} pt")
                # 즐겨찾기 버튼 (다음 단계 시뮬레이터와 연동할 준비)
                st.button("⭐ 즐겨찾기", key=f"fav_{row['프로그램명']}")