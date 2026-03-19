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
# 위험도 계산
# -------------------------
risk_score = (
    (heat_index * 0.4) +
    (elderly_ratio * 0.2) +
    (living_alone_ratio * 0.2) +
    (shelter_distance * 0.2)
)

if heat_index >= 35:
    risk_score *= 1.3

st.metric("🔥 현재 위험 점수", round(risk_score, 2))

# -------------------------
# 가상 지역 데이터
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
tab1, tab2, tab3, tab4 = st.tabs([
    "🌡 체감온도 분석",
    "🏠 쉼터 접근성",
    "👵 취약성 분석",
    "🗺 지역 지도"
])

# =========================
# 1️⃣ 체감온도 분석
# =========================
with tab1:
    st.subheader("체감온도에 따른 온열질환 위험 변화")

    temps = np.arange(25, 46)
    risk_curve = []

    for t in temps:
        score = (t * 0.4) + (elderly_ratio * 0.2) + (living_alone_ratio * 0.2) + (shelter_distance * 0.2)
        if t >= 35:
            score *= 1.3
        risk_curve.append(score)

    df = pd.DataFrame({"체감온도": temps, "위험 점수": risk_curve})

    fig = px.line(
        df,
        x="체감온도",
        y="위험 점수",
        title="체감온도와 위험도의 관계 (임계점: 35도)"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 2️⃣ 쉼터 접근성
# =========================
with tab2:
    st.subheader("쉼터 접근 시간에 따른 위험도 변화")

    distances = np.arange(1, 31)
    risk_dist = []

    for d in distances:
        score = (heat_index * 0.4) + (elderly_ratio * 0.2) + (living_alone_ratio * 0.2) + (d * 0.2)
        if heat_index >= 35:
            score *= 1.3
        risk_dist.append(score)

    df = pd.DataFrame({"접근 시간": distances, "위험 점수": risk_dist})

    fig = px.line(
        df,
        x="접근 시간",
        y="위험 점수",
        title="쉼터 접근성과 위험도의 관계"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 3️⃣ 취약성 분석
# =========================
with tab3:
    st.subheader("취약성 요인별 위험 기여도")

    df = pd.DataFrame({
        "요인": ["체감온도", "노인 비율", "독거노인 비율", "쉼터 거리"],
        "기여도": [
            heat_index * 0.4,
            elderly_ratio * 0.2,
            living_alone_ratio * 0.2,
            shelter_distance * 0.2
        ]
    })

    fig = px.bar(
        df,
        x="요인",
        y="기여도",
        title="요인별 위험 기여도"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 4️⃣ 지도
# =========================
with tab4:
    st.subheader("지역별 온도 지도")

    fig = px.scatter_mapbox(
        data,
        lat="위도",
        lon="경도",
        size="기온",
        color="기온",
        hover_name="지역",
        zoom=5,
        height=map_size
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)
