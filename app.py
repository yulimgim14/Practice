import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="폭염 분석 대시보드", layout="wide")

st.title("🔥 폭염 취약성 분석 대시보드")

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
# 지도 크기 조절
# -------------------------
st.sidebar.header("🗺 지도 설정")
map_size = st.sidebar.slider("지도 크기", 400, 1000, 600)

# -------------------------
# 탭 구성
# -------------------------
tab1, tab2 = st.tabs(["📊 지역 온도 분석", "🗺 지도 시각화"])

# =========================
# 📊 1. 지역 온도 그래프
# =========================
with tab1:
    st.subheader("지역별 기온 비교")

    fig = px.bar(
        data,
        x="지역",
        y="기온",
        labels={"지역": "지역", "기온": "기온 (°C)"},
        title="지역별 온도 차이"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 🗺 2. 지도 시각화
# =========================
with tab2:
    st.subheader("지역별 온도 지도")

    fig_map = px.scatter_mapbox(
        data,
        lat="위도",
        lon="경도",
        size="기온",
        color="기온",
        hover_name="지역",
        hover_data={"기온": True},
        zoom=5,
        height=map_size
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig_map, use_container_width=True)
