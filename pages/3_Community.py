import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 💡 멀티 페이지 앱이므로 st.set_page_config는 메인(app.py)에서만 실행되도록 여기서는 제외했습니다.
st.title("💬 재학생 익명 솔직 후기")
st.markdown("에브리타임 뺨치는 **다차원 별점 시스템**! 선배들의 생생한 비교과 꿀팁을 확인하세요.")

# --- 1. 데이터 로드 및 초기화 (빈 파일 에러 완벽 방지) ---
DATA_PATH = "data/reviews.csv"

@st.cache_data(ttl=0)  # 항상 최신 데이터를 실시간으로 읽어옴
def load_reviews():
    # 파일이 존재하고, 크기가 0바이트보다 클 때만 정상 로드
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        try:
            return pd.read_csv(DATA_PATH)
        except Exception:
            # 혹시 모를 로드 에러 대비 안전장치
            pass
            
    # 파일이 없거나 텅 비어있다면 에러를 내는 대신 기본 컬럼 구조를 가진 데이터프레임 자동 생성
    return pd.DataFrame(columns=["작성일", "프로그램명", "총점", "꿀지수", "혜자지수", "한줄평", "상세후기"])

df_reviews = load_reviews()

# --- 2. 후기 작성 폼 (에타 스타일 다차원 평가) ---
with st.expander("✍️ 새로운 익명 후기 남기기", expanded=False):
    with st.form("review_form"):
        # 학과별 연동을 위한 기본 프로그램 리스트
        program_list = ["파이썬 기초 특강", "도서관 근로 장학생", "AI 해커톤", "글로벌 멘토링", "취업 면접 컨설팅", "상상부기 피어코칭"]
        selected_prog = st.selectbox("어떤 프로그램의 후기를 남기시겠어요?", program_list)
        
        st.markdown("##### ⭐️ 에타 스타일 다차원 별점 평가")
        col1, col2, col3 = st.columns(3)
        with col1:
            overall = st.slider("🌟 총점 (전반적 만족도)", 1, 5, 5)
        with col2:
            honey = st.slider("🍯 꿀지수 (난이도/쉬운 정도)", 1, 5, 5, help="5점에 가까울수록 과제가 적고 날로 먹는 꿀 비교과!")
        with col3:
            useful = st.slider("💖 혜자지수 (유용성/만족도)", 1, 5, 5, help="5점에 가까울수록 취업이나 학점에 진짜 도움 되는 프로그램!")
            
        st.markdown("##### 📝 리뷰 내용 입력")
        short_review = st.text_input("한줄평", placeholder="예: 진짜 꿀입니다. 무조건 들으세요!")
        detail_review = st.text_area("상세 후기", placeholder="수업 방식, 출석 체크 강도, 시험/과제 유무 등 후배들에게 도움이 될 내용을 적어주세요.")
        
        submitted = st.form_submit_button("익명으로 등록하기 🚀")
        
        if submitted:
            if not short_review or not detail_review:
                st.error("⚠️ 한줄평과 상세 후기를 모두 입력해 주세요!")
            else:
                # 새로운 리뷰 행 생성
                new_review = {
                    "작성일": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "프로그램명": selected_prog,
                    "총점": overall,
                    "꿀지수": honey,
                    "혜자지수": useful,
                    "한줄평": short_review,
                    "상세후기": detail_review
                }
                
                # 기존 데이터에 합치기
                new_df = pd.DataFrame([new_review])
                updated_df = pd.concat([df_reviews, new_df], ignore_index=True)
                
                # data 폴더가 없으면 자동 생성 후 저장 (utf-8-sig로 엑셀 깨짐 방지)
                os.makedirs("data", exist_ok=True)
                updated_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
                
                st.success("🎉 후기가 성공적으로 등록되었습니다!")
                st.rerun()  # 화면 즉시 새로고침하여 리스트에 반영

# --- 3. 에타 스타일 리뷰 게시판 렌더링 ---
st.markdown("---")
st.subheader("👀 생생한 후기 모아보기")

if df_reviews.empty:
    st.info("아직 등록된 후기가 없습니다. 첫 번째 후기의 주인공이 되어보세요! 🐥")
else:
    # 최신순 정렬
    df_reviews = df_reviews.sort_values(by="작성일", ascending=False)
    
    # 프로그램별 필터링 기능
    filter_options = ["전체보기"] + list(df_reviews["프로그램명"].unique())
    filter_prog = st.selectbox("🎯 특정 프로그램 후기만 보기", filter_options)
    
    display_df = df_reviews if filter_prog == "전체보기" else df_reviews[df_reviews["프로그램명"] == filter_prog]

    # 리뷰 카드 UI 출력
    for index, row in display_df.iterrows():
        with st.container(border=True):
            st.markdown(f"#### 📌 {row['프로그램명']}")
            st.markdown(f"**\"{row['한줄평']}\"**")
            
            # 다차원 별점 시각화 (★ 기호 활용)
            st.markdown(
                f"🌟 **총점**: {'★' * int(row['총점'])}{'☆' * (5 - int(row['총점']))} | "
                f"🍯 **꿀지수**: {'★' * int(row['꿀지수'])}{'☆' * (5 - int(row['꿀지수']))} | "
                f"💖 **혜자지수**: {'★' * int(row['혜자지수'])}{'☆' * (5 - int(row['혜자지수']))}"
            )
            st.caption(f"📅 작성일: {row['작성일']} | 👤 익명 재학생")
            
            # 에타 특유의 회색 박스 느낌으로 상세 후기 노출
            st.info(row['상세후기'])