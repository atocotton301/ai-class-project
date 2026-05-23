import streamlit as st
import pandas as pd
from utils.recommender import get_sorted_programs

st.title("📅 맞춤형 비교과 큐레이션")

# 1. 로그인 상태 확인
if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면(온보딩)에서 먼저 프로필을 설정해 주세요!")
    st.stop()

# 유저 프로필 정보 연동
user_profile = st.session_state.user_profile
user_name = user_profile.get("name", "학생")
user_categories = user_profile.get("categories", [])

st.write(f"**{user_name}**님이 관심 있는 분야의 프로그램들입니다.")

# 2. 더미 데이터 세팅 (카테고리명 완벽 일치)
mock_data = {
    "프로그램명": ["파이썬 기초 특강", "도서관 근로 장학생", "AI 해커톤", "글로벌 멘토링", "취업 면접 컨설팅", "상상부기 피어코칭"],
    "카테고리": [
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "사회봉사 및 인성 함양 (교내외 봉사활동, 멘토링 프로그램)", 
        "창의융합역량 프로그램 (IT 기초, 전공 융합, 기술 트렌드 등)", 
        "글로벌역량 프로그램 (어학, 교환학생, 다문화 이해 등)",
        "취·창업 지원 프로그램 (포트폴리오, 면접 컨설팅, 창업 동아리)",
        "학습인프라/학습법 강화 (학습 튜터링, 상상부기 피어코칭)"
    ],
    "포인트": [30, 100, 200, 150, 50, 80],
    "소요시간(시간)": [10, 50, 48, 30, 5, 20],
    "꿀지수": [4.5, 3.0, 2.0, 4.0, 3.5, 4.5],
    "혜자지수": [4.0, 3.5, 5.0, 4.5, 4.0, 4.0]
}
df = pd.DataFrame(mock_data)

# 3. 정렬 옵션 UI
sort_option = st.radio(
    "어떤 기준으로 정렬할까요?",
    ["🔥 포인트 높은 순", "⏱️ 시간 대비 가성비 순", "🍯 꿀지수 (난이도) 높은 순", "💖 혜자지수 (만족도) 높은 순"],
    horizontal=True
)

# 4. 정렬 함수 실행
sorted_df = get_sorted_programs(df, user_categories, sort_option)

st.markdown("### 📋 추천 리스트")
if len(sorted_df) == 0:
    st.error("앗! 선택하신 관심 분야와 일치하는 데이터가 현재 등록되어 있지 않습니다.")
else:
    # 화면 렌더링 충돌을 방지하는 가장 안정적인 table 표기법 사용
    st.table(sorted_df)