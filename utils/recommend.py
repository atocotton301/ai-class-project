import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import os

st.set_page_config(page_title="HanS-Plan AI", page_icon="📅", layout="centered")
st.title("📅 HanS-Plan AI")
st.subheader("맞춤형 비교과 프로그램 추천")

# 현재 실행 파일 위치 기준으로 user_profile.json 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "user_profile.json")

# 사용자 프로필 불러오기
with open(DATA_PATH, "r", encoding="utf-8") as f:
    profile = json.load(f)

st.write("### 👤 사용자 정보")
st.write(f"- 이름: {profile['name']}")
st.write(f"- 학번: {profile['student_id']}")
st.write(f"- 학과: {profile['major']}")
st.write(f"- 이메일: {profile['email']}")

# 웹 데이터 가져오기
url = "https://hsportal.hansung.ac.kr/ko/program/all/list/all/1"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

programs = []
for item in soup.select('div[data-module="eco"][data-role="item"]'):
    title = item.select_one('.title_wrap .title').text.strip() if item.select_one('.title_wrap .title') else ""
    institution = item.select_one('.institution').text.strip() if item.select_one('.institution') else ""
    hits = item.select_one('.hit .hit').text.strip() if item.select_one('.hit .hit') else ""
    raw_points = item.select_one('label').text.strip() if item.select_one('label') else ""
    dates = item.select('small.date_layer')
    apply_period = dates[0].get_text(" ", strip=True) if len(dates) > 0 else ""
    operate_period = dates[1].get_text(" ", strip=True) if len(dates) > 1 else ""
    # "운영:" 접두어 제거
    if operate_period.startswith("운영:"):
        operate_period = operate_period.replace("운영:", "").strip()
    progress = item.select_one('.progress').get_text(" ", strip=True) if item.select_one('.progress') else ""
    certified = "인재인증" if item.select_one('.certified') else "미인증"

    # D-day 추출 및 분리
    d_day = ""
    points = raw_points
    if "D-" in raw_points:
        parts = raw_points.split()
        for p in parts:
            if p.startswith("D-"):
                d_day = p
            elif p.startswith("p"):
                points = p  # 포인트만 남김

    # 신청기간에 D-day 추가
    if d_day:
        apply_period = f"{apply_period} ({d_day})"

    programs.append({
        "title": title,
        "institution": institution,
        "apply_period": apply_period,
        "operate_period": operate_period,
        "points": points,
        "progress": progress,
        "certified": certified,
        "hits": hits
    })

# 사용자 입력 위젯 추가
min_score = st.slider("추천 점수 역치(1~5)", min_value=1, max_value=5, value=3)
max_recommend = st.slider("최대 추천 개수", min_value=1, max_value=10, value=5)

# 관심 분야 필터링 (5가지 항목 기반 점수 계산)
desired_categories = [c.lower() for c in profile.get("categories", [])]
desired_external = [c.lower() for c in profile.get("external_activities", [])]
desired_surveys = [c.lower() for c in profile.get("surveys", [])]
desired_tags = [c.lower() for c in profile.get("tags", [])]
desired_operators = [c.lower() for c in profile.get("operators", [])]

scored_programs = []

for prog in programs:
    score = 0
    # 1. 프로그램 분류(title)
    for cat in desired_categories:
        if cat in prog["title"].lower():
            score += 1
    # 2. 교‧비교과 활동(points)
    for act in desired_external:
        if act in prog["points"].lower():
            score += 1
    # 3. 진단/설문(apply_period, operate_period)
    for survey in desired_surveys:
        if survey in prog["apply_period"].lower() or survey in prog["operate_period"].lower():
            score += 1
    # 4. 태그(title, institution)
    for tag in desired_tags:
        if tag in prog["title"].lower() or tag in prog["institution"].lower():
            score += 1
    # 5. 운영기관(institution)
    for op in desired_operators:
        if op in prog["institution"].lower():
            score += 1

    prog["score"] = score
    scored_programs.append(prog)

# 점수 조건 이상만 추천, 점수 높은 순으로 정렬
recommended = [p for p in scored_programs if p["score"] >= min_score]
recommended.sort(key=lambda x: x["score"], reverse=True)

# 최대 추천 개수 제한
recommended = recommended[:max_recommend]

st.write("### 🔍 추천 프로그램 목록")
if recommended:
    for prog in recommended:
        st.markdown(f"**📌 {prog['title']}** (추천 점수: {prog['score']})")
        st.write(f"- 기관: {prog['institution']}")
        st.write(f"- 신청기간: {prog['apply_period']}")
        st.write(f"- 운영기간: {prog['operate_period']}")
        st.write(f"- 포인트: {prog['points']}")
        st.write(f"- 참여 인원: {prog['progress']}")
        st.write(f"- 인재인증 여부: {prog['certified']}")
        st.write(f"- 조회수: {prog['hits']}")
        st.markdown("---")
else:
    st.warning("⚠️ 관심 분야에 해당하는 추천 프로그램이 없습니다.")
