import streamlit as st
import json
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

st.set_page_config(page_title="HanS-Plan AI", page_icon="📅", layout="wide")
st.title("📅 HanS-Plan AI")
st.subheader("🎯 AI 기반 맞춤형 비교과 프로그램 추천")

# ==========================================
# 1. 사용자 프로필 불러오기
# ==========================================
if 'login_id' not in st.session_state:
    st.warning("⚠️ 메인 화면(앱)에서 로그인 또는 온보딩을 먼저 완료해 주세요.")
    st.stop()

PROFILE_DB_PATH = f"data/{st.session_state.login_id}_profile.json"

try:
    with open(PROFILE_DB_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)
except FileNotFoundError:
    st.error("❌ 사용자 프로필을 찾을 수 없습니다. 먼저 프로필을 설정해주세요.")
    st.stop()

st.write("### 👤 사용자 정보")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info(f"📛 **{profile['name']}**")
with col2:
    st.info(f"🆔 **{profile['student_id']}**")
with col3:
    st.info(f"📚 **{profile['major']}**")
with col4:
    st.info(f"📧 **{profile['email']}**")

# ==========================================
# 2. 한성대 포털에서 비교과 프로그램 크롤링
# ==========================================
@st.cache_data(ttl=3600)  # 1시간마다 갱신
def fetch_programs_from_portal():
    """
    한성대 포털에서 비교과 프로그램 정보를 크롤링합니다.
    페이지 1~4에서 모든 프로그램을 수집합니다.
    """
    base_urls = [
        "https://hsportal.hansung.ac.kr/ko/program/all/list/0/1",
        "https://hsportal.hansung.ac.kr/ko/program/all/list/0/2",
        "https://hsportal.hansung.ac.kr/ko/program/all/list/0/3",
        "https://hsportal.hansung.ac.kr/ko/program/all/list/0/4"
    ]
    
    programs = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for page_url in base_urls:
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 프로그램 항목 선택자
            items = soup.select('div[data-module="eco"][data-role="item"]')
            
            for item in items:
                try:
                    # 프로그램명
                    title_elem = item.select_one('.title_wrap .title')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # 운영기관
                    institution_elem = item.select_one('.institution')
                    institution = institution_elem.text.strip() if institution_elem else ""
                    
                    # 조회수
                    hits_elem = item.select_one('.hit .hit')
                    hits = hits_elem.text.strip() if hits_elem else "0"
                    
                    # 포인트 및 D-day
                    label_elem = item.select_one('label')
                    raw_points = label_elem.text.strip() if label_elem else ""
                    
                    # 신청기간과 운영기간
                    dates = item.select('small.date_layer')
                    apply_period = dates[0].get_text(" ", strip=True) if len(dates) > 0 else ""
                    operate_period = dates[1].get_text(" ", strip=True) if len(dates) > 1 else ""
                    
                    # "운영:" 접두어 제거
                    if operate_period.startswith("운영:"):
                        operate_period = operate_period.replace("운영:", "").strip()
                    
                    # 진행 상황
                    progress_elem = item.select_one('.progress')
                    progress = progress_elem.get_text(" ", strip=True) if progress_elem else ""
                    
                    # 인재인증 여부
                    certified = "인재인증" if item.select_one('.certified') else "미인증"
                    
                    # D-day와 포인트 분리
                    d_day = ""
                    points = raw_points
                    if "D-" in raw_points:
                        parts = raw_points.split()
                        for p in parts:
                            if p.startswith("D-"):
                                d_day = p
                            elif p.startswith("p") or "pt" in p:
                                points = p
                    
                    # 신청기간에 D-day 추가
                    if d_day:
                        apply_period = f"{apply_period} ({d_day})"
                    
                    # 빈 제목인 경우 스킵
                    if not title:
                        continue
                    
                    programs.append({
                        "title": title,
                        "institution": institution,
                        "apply_period": apply_period,
                        "operate_period": operate_period,
                        "points": points,
                        "progress": progress,
                        "certified": certified,
                        "hits": hits,
                        "description": f"{title} - {institution}"  # TF-IDF용 설명
                    })
                
                except Exception as e:
                    continue
        
        except Exception as e:
            st.warning(f"⚠️ 페이지 로드 실패: {page_url}")
            continue
    
    return programs

# ==========================================
# 3. 사용자 프로필 텍스트 전처리
# ==========================================
def create_user_profile_text(profile):
    """
    사용자 프로필 데이터를 하나의 텍스트로 결합
    - major: 학과 정보
    - certifications: 자격증 목표
    - categories: 관심 분야
    """
    text_parts = []
    
    # 학과 정보
    if profile.get('major'):
        text_parts.append(profile['major'])
    
    # 자격증 목표
    if profile.get('certifications'):
        text_parts.append(' '.join(profile['certifications']))
    
    # 관심 분야
    if profile.get('categories'):
        text_parts.append(' '.join(profile['categories']))
    
    user_profile_text = ' '.join(text_parts)
    return user_profile_text

# ==========================================
# 4. 시간 충돌 검사 함수
# ==========================================
def time_to_minutes(time_str):
    """시간 문자열(HH:MM)을 분 단위로 변환"""
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except:
        return 0

def check_time_conflict(operate_period_str, timetable):
    """
    운영기간 문자열과 사용자의 수업 시간이 겹치는지 확인
    (운영기간에서 요일과 시간 정보 추출 시도)
    """
    if not operate_period_str or not timetable:
        return False
    
    # 요일 매핑
    day_mapping = {"월": "월", "화": "화", "수": "수", "목": "목", "금": "금", "토": "토"}
    
    try:
        # 운영기간에서 요일과 시간 추출 시도
        for day_ko in day_mapping.keys():
            if day_ko in operate_period_str:
                # 해당 요일의 수업이 있는지 확인
                for class_info in timetable:
                    if class_info.get('요일') == day_ko:
                        return True  # 같은 요일에 수업이 있으면 충돌 가능성
    except:
        pass
    
    return False

# ==========================================
# 5. TF-IDF 기반 유사도 추천 알고리즘
# ==========================================
def recommend_programs_tfidf(profile, programs, top_n=10):
    """
    TF-IDF와 코사인 유사도를 활용한 프로그램 추천
    
    Parameters:
    - profile: 사용자 프로필
    - programs: 비교과 프로그램 리스트
    - top_n: 추천할 프로그램 개수
    
    Returns:
    - 추천 프로그램 리스트 (유사도 점수 포함)
    """
    
    if not programs:
        return [], [], ""
    
    # 1. 사용자 프로필 텍스트 생성
    user_profile_text = create_user_profile_text(profile)
    
    # 2. 프로그램 텍스트 생성 (title + institution + apply_period + operate_period)
    program_texts = [
        f"{prog['title']} {prog['institution']} {prog['apply_period']} {prog['operate_period']}"
        for prog in programs
    ]
    
    # 3. TF-IDF 벡터화 (한글 처리를 위해 char n-gram 사용)
    try:
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), lowercase=True)
        
        # 사용자 프로필과 프로그램들을 함께 벡터화
        all_texts = [user_profile_text] + program_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # 4. 코사인 유사도 계산
        user_vector = tfidf_matrix[0]
        program_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(user_vector, program_vectors)[0]
    except Exception as e:
        st.warning(f"⚠️ 유사도 계산 오류: {e}")
        similarities = np.random.random(len(programs))
    
    # 5. 프로그램에 유사도 점수 추가
    for i, prog in enumerate(programs):
        prog['similarity_score'] = float(similarities[i])
    
    # 6. 시간표 충돌 필터링
    timetable = profile.get('timetable', [])
    filtered_programs = []
    conflict_programs = []
    
    for prog in programs:
        has_conflict = check_time_conflict(prog['operate_period'], timetable)
        if has_conflict:
            conflict_programs.append(prog)
        else:
            filtered_programs.append(prog)
    
    # 7. 유사도 점수로 정렬 및 상위 top_n 선택
    filtered_programs.sort(key=lambda x: x['similarity_score'], reverse=True)
    recommended = filtered_programs[:top_n]
    
    return recommended, conflict_programs, user_profile_text

# ==========================================
# 6. 프로그램 데이터 로드
# ==========================================
st.markdown("---")

# 캐시된 데이터 사용 또는 새로 가져오기
with st.spinner("🔄 한성대 포털에서 프로그램 정보를 불러오는 중..."):
    programs = fetch_programs_from_portal()

if not programs:
    st.error("❌ 포털에서 프로그램 정보를 불러올 수 없습니다.")
    st.info("💡 잠시 후 다시 시도해주세요.")
    st.stop()

st.success(f"✅ {len(programs)}개의 비교과 프로그램을 로드했습니다.")

# ==========================================
# 7. UI 슬라이더 및 추천 실행
# ==========================================
col1, col2 = st.columns(2)
with col1:
    top_n = st.slider("📊 추천할 프로그램 개수", min_value=1, max_value=min(20, len(programs)), value=10)
with col2:
    show_conflicts = st.checkbox("⚠️ 시간 겹침 프로그램도 보기", value=False)

# ==========================================
# 8. 추천 실행 및 결과 표시
# ==========================================
if st.button("🚀 맞춤형 추천 프로그램 조회", use_container_width=True):
    with st.spinner("🔍 AI 기반 프로그램 분석 중..."):
        recommended, conflict_programs, user_profile_text = recommend_programs_tfidf(
            profile,
            programs,
            top_n=top_n
        )
    
    # 사용자 프로필 분석 결과 표시
    st.markdown("---")
    st.write("### 📋 사용자 프로필 분석")
    with st.container(border=True):
        st.write(f"**생성된 프로필 문장:**")
        st.text(user_profile_text)
        st.write(f"**프로필 길이:** {len(user_profile_text)} 문자")
        st.write(f"**관심 분야:** {', '.join(profile.get('categories', []))}")
        st.write(f"**목표 자격증:** {', '.join(profile.get('certifications', []))}")
    
    # 추천 프로그램 결과
    st.markdown("---")
    st.write(f"### 🎯 추천 프로그램 ({len(recommended)}개)")
    
    if recommended:
        # 테이블 형식으로 표시
        recommendation_data = []
        for idx, prog in enumerate(recommended, 1):
            recommendation_data.append({
                "순위": f"#{idx}",
                "프로그램명": prog['title'],
                "운영기관": prog['institution'],
                "신청기간": prog['apply_period'][:30] + "..." if len(prog['apply_period']) > 30 else prog['apply_period'],
                "포인트": prog['points']
            })
        
        df_recommendations = pd.DataFrame(recommendation_data)
        st.dataframe(df_recommendations, use_container_width=True, hide_index=True)
        
        # 프로그램 상세 정보
        st.write("### 📌 프로그램 상세정보")
        for idx, prog in enumerate(recommended, 1):
            with st.expander(f"[{idx}] {prog['title']}", expanded=(idx==1)):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**운영기관:** {prog['institution']}")
                    st.write(f"**포인트:** {prog['points']}")
                    st.write(f"**진행상황:** {prog['progress']}")
                with col2:
                    st.write(f"**인재인증:** {prog['certified']}")
                    st.write(f"**조회수:** {prog['hits']}")
                
                st.markdown("**신청기간:**")
                st.info(prog['apply_period'])
                
                st.markdown("**운영기간:**")
                st.info(prog['operate_period'])
    else:
        st.warning("⚠️ 추천할 프로그램이 없습니다.")
    
    # 시간 충돌 프로그램 표시 (옵션)
    if show_conflicts and conflict_programs:
        st.markdown("---")
        st.write(f"### ⚠️ 시간 겹침 프로그램 ({len(conflict_programs)}개)")
        st.info("💡 아래 프로그램들은 운영 시간이 수업과 겹칠 가능성이 있습니다.")
        
        conflict_data = []
        for idx, prog in enumerate(conflict_programs[:10], 1):  # 최대 10개만 표시
            conflict_data.append({
                "프로그램명": prog['title'],
                "운영기관": prog['institution'],
                "운영기간": prog['operate_period'][:30] + "..." if len(prog['operate_period']) > 30 else prog['operate_period']
            })
        
        if conflict_data:
            df_conflicts = pd.DataFrame(conflict_data)
            st.dataframe(df_conflicts, use_container_width=True, hide_index=True)
    
    # 통계 정보
    st.markdown("---")
    st.write("### 📊 추천 통계")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("추천된 프로그램", len(recommended))
    with col2:
        st.metric("시간 충돌 프로그램", len(conflict_programs))
    with col3:
        st.metric("총 프로그램 수", len(programs))

# ==========================================
# 9. 전체 프로그램 목록 (참고용)
# ==========================================
st.markdown("---")
if st.checkbox("📋 전체 프로그램 목록 보기", value=False):
    st.write(f"### 전체 비교과 프로그램 ({len(programs)}개)")
    
    all_programs_data = []
    for prog in programs[:50]:  # 처음 50개만 표시
        all_programs_data.append({
            "프로그램명": prog['title'],
            "운영기관": prog['institution'],
            "포인트": prog['points'],
            "진행상황": prog['progress'],
            "인재인증": prog['certified']
        })
    
    df_all = pd.DataFrame(all_programs_data)
    st.dataframe(df_all, use_container_width=True, hide_index=True)
    
    if len(programs) > 50:
        st.info(f"💡 표시된 프로그램: 50개 / 전체: {len(programs)}개")
