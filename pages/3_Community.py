import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("💬 재학생 익명 솔직 후기")

# ==========================================
# 🚨 로그인 상태 확인
# ==========================================
if 'is_logged_in' not in st.session_state or not st.session_state.is_logged_in:
    st.warning("⚠️ 메인 화면에서 먼저 프로필을 설정해 주세요!")
    st.stop()

# ==========================================
# 1. 데이터 로드 및 초기화 (기존 데이터 완벽 연동)
# ==========================================
# 유저의 기존 파일명인 'review.csv'로 경로 수정
DATA_PATH = "data/review.csv"

@st.cache_data(ttl=0)
def load_reviews():
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        try:
            df = pd.read_csv(DATA_PATH)
            # 혹시 예전 코드 테스트로 인해 '비교과명' 컬럼이 섞여 있다면 '프로그램명'으로 통일
            if '비교과명' in df.columns:
                df = df.rename(columns={'비교과명': '프로그램명'})
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["작성일", "프로그램명", "총점", "꿀지수", "혜자지수", "한줄평", "상세후기"])

df_reviews = load_reviews()

program_list = [
    "파이썬 기초 특강", "도서관 근로 장학생", "AI 해커톤", "글로벌 멘토링", 
    "취업 면접 컨설팅", "상상부기 피어코칭", "인공지능 트렌드 세미나", "기초 코딩 역량 강화"
]

# ==========================================
# 📐 레이아웃 분할 (좌측 내 정보 / 우측 커뮤니티)
# ==========================================
col_left, col_spacing, col_right = st.columns([1.2, 0.1, 2.7])

# ------------------------------------------
# [좌측 영역] 내 비교과 (요청하신 대로 공란 처리)
# ------------------------------------------
with col_left:
    st.markdown("#### 📂 내 비교과")
    
    # 다른 페이지와 어울리는 깔끔한 박스 UI
    with st.container(border=True):
        st.info("아직 신청 및 수료한 비교과 프로그램이 없습니다.")
        st.caption("💡 캘린더에서 관심 있는 프로그램을 신청하면 이곳에 목록이 나타납니다.")

# ------------------------------------------
# [우측 영역] 비교과 리뷰 리스트 및 작성
# ------------------------------------------
with col_right:
    # 1. 후기 작성 폼
    with st.expander("✍️ 새로운 익명 후기 / 비교과 리뷰 남기기", expanded=False):
        with st.form("review_form"):
            selected_prog = st.selectbox("어떤 비교과 프로그램의 후기를 남기시겠어요?", program_list)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                overall = st.slider("🌟 총점 (만족도)", 1, 5, 5)
            with col2:
                honey = st.slider("🍯 꿀지수 (난이도/수월함)", 1, 5, 5)
            with col3:
                useful = st.slider("💖 혜자지수 (유용성)", 1, 5, 5)
                
            short_review = st.text_input("한줄평", placeholder="예) 강사님 강의력 최고, 무조건 들으세요!")
            detail_review = st.text_area("상세 후기", placeholder="출석 체크 방식, 과제 유무, 실무 도움 정도 등 상세히 적어주세요.")
            
            if st.form_submit_button("익명으로 등록하기 🚀"):
                if not short_review or not detail_review:
                    st.error("⚠️ 한줄평과 상세 후기를 모두 입력해 주세요!")
                else:
                    new_review = {
                        "작성일": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "프로그램명": selected_prog,
                        "총점": overall,
                        "꿀지수": honey,
                        "혜자지수": useful,
                        "한줄평": short_review,
                        "상세후기": detail_review
                    }
                    updated_df = pd.concat([df_reviews, pd.DataFrame([new_review])], ignore_index=True)
                    os.makedirs("data", exist_ok=True)
                    updated_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
                    st.success("🎉 비교과 후기가 성공적으로 등록되었습니다!")
                    st.rerun()

    # 2. 리뷰 리스트 화면 출력
    st.markdown("#### 👀 생생한 후기 모아보기")
    
    if df_reviews.empty:
        st.info("아직 등록된 비교과 후기가 없습니다. 첫 번째 후기의 주인공이 되어보세요! 🐥")
    else:
        # 최신순 정렬
        df_reviews = df_reviews.sort_values(by="작성일", ascending=False)
        
        # 특정 비교과 검색 필터
        filter_options = ["전체 리뷰 보기"] + program_list
        filter_prog = st.selectbox("필터", filter_options, label_visibility="collapsed")
        
        display_df = df_reviews if filter_prog == "전체 리뷰 보기" else df_reviews[df_reviews["프로그램명"] == filter_prog]

        if display_df.empty:
            st.info("해당 프로그램에 대한 후기가 아직 없습니다.")
        else:
            for index, row in display_df.iterrows():
                # 꿀/혜자 지수 기본값 방어 코드
                honey_val = row.get('꿀지수', 0)
                useful_val = row.get('혜자지수', 0)
                
                # Streamlit 네이티브 UI로 깔끔하게 변경된 리뷰 카드
                with st.container(border=True):
                    c_title, c_stars = st.columns([3, 1])
                    with c_title:
                        hot_badge = "🔥" if row['총점'] >= 4 else "💬"
                        st.markdown(f"**{hot_badge} {row['프로그램명']}**")
                    with c_stars:
                        stars_html = "★" * int(row['총점']) + "☆" * (5 - int(row['총점']))
                        st.markdown(f"<div style='text-align: right; color: #FFD700; letter-spacing: 2px;'>{stars_html}</div>", unsafe_allow_html=True)
                    
                    st.write(f"\"{row['한줄평']}\"")
                    st.caption(f"📅 {row['작성일']} | 익명 | 👍 추천 {int(row['총점']) * 2 + 1}")
                    
                    st.info(row['상세후기'])
                    
                    # 하단 뱃지
                    st.markdown(f"""
                        <span style='background-color:#f0f2f6; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; color:#555; margin-right: 5px;'>
                            🍯 꿀지수: {honey_val}/5
                        </span>
                        <span style='background-color:#f0f2f6; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; color:#555;'>
                            💖 혜자지수: {useful_val}/5
                        </span>
                    """, unsafe_allow_html=True)