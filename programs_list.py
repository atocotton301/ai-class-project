import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import os

# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="비교과 프로그램 목록",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS 스타일 (Apple 스타일 - 간단한 버전)
# ==========================================
st.markdown("""
<style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    .block-container {
        padding-top: 2rem;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 세션 상태 초기화 (효율적인 상태 관리)
# ==========================================
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = set()

if "filter_mode" not in st.session_state:
    st.session_state.filter_mode = "all"  # "all" 또는 "bookmarks"

# ==========================================
# 한성대 포털에서 프로그램 데이터 가져오기
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_programs():
    """한성대 포털에서 비교과 프로그램 정보를 크롤링합니다."""
    programs = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    page = 1
    while page <= 10:  # 최대 10페이지까지만 탐색 (안전장치)
        try:
            page_url = f"https://hsportal.hansung.ac.kr/ko/program/all/list/all/1/{page}"
            response = requests.get(page_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select('div[data-module="eco"][data-role="item"]')
            
            # 더 이상 프로그램이 없으면 종료
            if not items:
                break
                
            for item in items:
                try:
                    title_elem = item.select_one('.title_wrap .title')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    institution_elem = item.select_one('.institution')
                    institution = institution_elem.text.strip() if institution_elem else ""
                    
                    hits_elem = item.select_one('.hit .hit')
                    hits = hits_elem.text.strip() if hits_elem else "0"
                    
                    label_elem = item.select_one('label')
                    
                    dates = item.select('small.date_layer')
                    apply_period = dates[0].get_text(" ", strip=True) if len(dates) > 0 else ""
                    operate_period = dates[1].get_text(" ", strip=True) if len(dates) > 1 else ""
                    
                    if operate_period.startswith("운영:"):
                        operate_period = operate_period.replace("운영:", "").strip()
                    
                    progress_elem = item.select_one('.progress')
                    progress = progress_elem.get_text(" ", strip=True) if progress_elem else ""
                    
                    certified = "인재인증" if item.select_one('.certified') else "미인증"
                    
                    # D-Day 및 포인트 추출 보완
                    d_day = ""
                    if label_elem:
                        d_day_elem = label_elem.select_one('b.lh_38')
                        if d_day_elem and "D-" in d_day_elem.text:
                            d_day = d_day_elem.text.strip()
                            
                    points = "0"
                    point_elem = item.select_one('i.point')
                    if point_elem and point_elem.next_sibling:
                        pt_text = str(point_elem.next_sibling).strip()
                        if pt_text:
                            points = pt_text + " pt"
                    
                    if d_day:
                        apply_period = f"{apply_period} ({d_day})"
                    
                    if not title:
                        continue
                    
                    programs.append({
                        "id": f"{title}_{len(programs)}",  # 고유 ID 생성
                        "title": title,
                        "institution": institution,
                        "apply_period": apply_period,
                        "operate_period": operate_period,
                        "points": points,
                        "progress": progress,
                        "certified": certified,
                        "hits": hits
                    })
                
                except Exception:
                    continue
            
            page += 1
            
        except Exception:
            # 에러 발생시 다음 페이지로 넘어가거나 종료
            page += 1
            continue
    
    return programs

# ==========================================
# 필터링 함수
# ==========================================
def get_displayed_programs():
    """현재 필터 모드에 따라 표시할 프로그램 리스트 반환"""
    if st.session_state.filter_mode == "bookmarks":
        return [p for p in programs if p['id'] in st.session_state.bookmarks]
    return programs

# ==========================================
# UI 구성
# ==========================================

# 헤더
st.title("📋 비교과 프로그램")
st.markdown("한성대학교 비교과 포인트 프로그램 목록")

# 데이터 로드
with st.spinner("🚀 최초 1회만 학교 서버에서 프로그램들을 가져오고 있어요! (이후엔 캐시로 바로 뜹니다) 🧚‍♀️✨"):
    programs = fetch_programs()

if not programs:
    st.error("❌ 프로그램 정보를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

# 통계
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("전체 프로그램", len(programs))

with col2:
    bookmarked_count = len(st.session_state.bookmarks)
    st.metric("즐겨찾기", f"⭐ {bookmarked_count}")

with col3:
    st.metric("조회수", "최신순")

st.divider()

# 필터 탭
filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 8])

with filter_col1:
    if st.button(
        "📋 전체 보기",
        use_container_width=True,
        key="filter_all",
        type="primary" if st.session_state.filter_mode == "all" else "secondary"
    ):
        st.session_state.filter_mode = "all"
        st.rerun()

with filter_col2:
    if st.button(
        "⭐ 즐겨찾기",
        use_container_width=True,
        key="filter_bookmarks",
        type="primary" if st.session_state.filter_mode == "bookmarks" else "secondary"
    ):
        st.session_state.filter_mode = "bookmarks"
        st.rerun()

# 필터 적용
displayed_programs = get_displayed_programs()
mode_title = "즐겨찾기" if st.session_state.filter_mode == "bookmarks" else "전체"

st.subheader(f"{mode_title} ({len(displayed_programs)}개)")

# ==========================================
# 프로그램 카드 렌더링
# ==========================================
if not displayed_programs:
    st.info("✨ 즐겨찾기한 프로그램이 없습니다. ⭐ 별 아이콘을 클릭하여 추가하세요.")
else:
    for program in displayed_programs:
        is_bookmarked = program['id'] in st.session_state.bookmarks
        star_icon = "⭐" if is_bookmarked else "☆"
        
        # 카드 생성
        with st.container(border=True):
            # 제목과 별 아이콘
            col_title, col_star = st.columns([20, 1])
            
            with col_title:
                st.markdown(f"### {program['title']}")
            
            with col_star:
                if st.button(
                    star_icon,
                    key=f"star_{program['id']}",
                    help="즐겨찾기에 추가/제거",
                    use_container_width=True
                ):
                    if program['id'] in st.session_state.bookmarks:
                        st.session_state.bookmarks.remove(program['id'])
                    else:
                        st.session_state.bookmarks.add(program['id'])
                    st.rerun()
            
            # 포인트만 표시 - 가로 정렬
            if program['points']:
                st.info(f"💰 {program['points']}")
            
            # 상세 정보
            st.divider()
            
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.markdown("**🏢 운영기관**")
                st.write(program['institution'])
                st.markdown("**📅 신청기간**")
                st.write(program['apply_period'])
            
            with info_col2:
                st.markdown("**⏰ 운영기간**")
                st.write(program['operate_period'])
                st.markdown("**👥 참여인원**")
                st.write(program['progress'])
            
            with info_col3:
                st.markdown("**👀 조회수**")
                st.write(program['hits'])
            
            st.divider()

st.markdown("---")

# 하단 정보
st.caption("💡 각 프로그램의 별(☆) 아이콘을 클릭하여 즐겨찾기에 추가하세요")
st.caption("🔄 원활한 이용을 위해 최신 데이터는 1시간마다 최초 접속 시 1회만 스크랩해옵니다.")
st.caption("📌 출처: 한성대학교 비교과 포인트 시스템")
