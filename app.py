import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="폭염 분석 대시보드", layout="wide")

st.title("🔥 폭염 취약성 분석 대시보드")

# -------------------------
# 입력
# -------------------------
st.sidebar.header("📊 입력 변수")

heat_index = st.sidebar.slider("체감온도 (°C)", 25, 45, 35)
elderly_ratio = st.sidebar.slider("노인 비율 (%)", 0, 50, 20)
living_alone_ratio = st.sidebar.slider("독거노인 비율 (%)", 0, 50, 15)
shelter_distance = st.sidebar.slider("쉼터 접근 시간 (분)", 1, 30, 10)

# 지도 크기
st.sidebar.header("🗺 지도 설정")
map_size = st.sidebar.slider("지도 크기", 400, 1000, 600)

# -------------------------
# 기본 위험도
# -------------------------
def calculate_risk(h, e, l, s):
    score = (h * 0.4) + (e * 0.2) + (l * 0.2) + (s * 0.2)
    if h >= 35:
        score *= 1.3
    return score

base_risk = calculate_risk(heat_index, elderly_ratio, living_alone_ratio, shelter_distance)

st.metric("🔥 현재 위험 점수", round(base_risk, 2))

# -------------------------
# 지역 데이터
# -------------------------
data = pd.DataFrame({
    "지역": ["서울", "부산", "대구", "인천", "광주", "대전", "울산"],
    "위도": [37.56, 35.18, 35.87, 37.45, 35.16, 36.35, 35.54],
    "경도": [126.97, 129.07, 128.60, 126.70, 126.85, 127.38, 129.31],
    "기온": [34, 32, 36, 33, 35, 34, 35]
})

# -------------------------
# 탭 구성
# -------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌡 체감온도",
    "🏠 접근성",
    "👵 취약성",
    "🗺 지도",
    "📊 정책 효과"
])

# =========================
# 정책 효과 탭
# =========================
with tab5:
    st.subheader("정책 적용 시 위험도 변화")

    policies = st.multiselect(
        "적용할 정책 선택",
        ["마이크로 쉼터 확대", "방문 케어 강화", "에너지 지원"]
    )

    # 정책 적용 변수
    new_heat = heat_index
    new_living = living_alone_ratio
    new_shelter = shelter_distance

    # 정책 반영 로직
    if "마이크로 쉼터 확대" in policies:
        new_shelter = max(1, shelter_distance - 5)

    if "방문 케어 강화" in policies:
        new_living = living_alone_ratio * 0.7

    if "에너지 지원" in policies:
        new_heat = heat_index * 0.9

    new_risk = calculate_risk(new_heat, elderly_ratio, new_living, new_shelter)

    # 결과 비교
    col1, col2 = st.columns(2)

    with col1:
        st.metric("기존 위험도", round(base_risk, 2))

    with col2:
        st.metric("정책 적용 후", round(new_risk, 2), delta=round(new_risk - base_risk, 2))

    # 변화 그래프
    df = pd.DataFrame({
        "상태": ["기존", "정책 적용"],
        "위험 점수": [base_risk, new_risk]
    })

    fig = px.bar(df, x="상태", y="위험 점수", title="정책 적용 효과 비교")

    st.plotly_chart(fig, use_container_width=True)

    st.info("✔ 정책 조합에 따라 위험도가 어떻게 감소하는지 확인할 수 있습니다.")
