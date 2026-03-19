import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 (윈도우 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="폭염 분석 대시보드", layout="wide")

st.title("🔥 폭염 취약성 분석 대시보드")
st.markdown("체감온도, 취약성, 접근성을 기반으로 온열질환 위험을 분석합니다.")

# -------------------------
# 입력 (사이드바)
# -------------------------
st.sidebar.header("📊 입력 변수")

heat_index = st.sidebar.slider("체감온도 (°C)", 25, 45, 35)
elderly_ratio = st.sidebar.slider("노인 비율 (%)", 0, 50, 20)
living_alone_ratio = st.sidebar.slider("독거노인 비율 (%)", 0, 50, 15)
shelter_distance = st.sidebar.slider("쉼터 접근 시간 (분)", 1, 30, 10)

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
# 탭 UI
# -------------------------
tab1, tab2, tab3 = st.tabs([
    "🌡 체감온도 분석",
    "🏠 쉼터 접근성",
    "👵 취약성 분석"
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

    fig, ax = plt.subplots()
    ax.plot(temps, risk_curve)
    ax.axvline(x=35, linestyle='--')

    ax.set_xlabel("체감온도 (°C)")
    ax.set_ylabel("온열질환 위험 점수")
    ax.set_title("체감온도와 위험도의 관계 (임계점: 35도)")

    st.pyplot(fig, use_container_width=True)

    st.info("✔ 체감온도 35도 이상에서 환자 급증 (임계점 구간)")

# =========================
# 2️⃣ 쉼터 접근성 분석
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

    fig, ax = plt.subplots()
    ax.plot(distances, risk_dist)

    ax.set_xlabel("쉼터까지 이동 시간 (분)")
    ax.set_ylabel("온열질환 위험 점수")
    ax.set_title("쉼터 접근성과 위험도의 관계")

    st.pyplot(fig, use_container_width=True)

    st.warning("✔ 15분 이상부터 정책 효과 급감")

# =========================
# 3️⃣ 취약성 분석
# =========================
with tab3:
    st.subheader("취약성 요인별 위험 기여도")

    features = ["체감온도", "노인 비율", "독거노인 비율", "쉼터 거리"]
    values = [
        heat_index * 0.4,
        elderly_ratio * 0.2,
        living_alone_ratio * 0.2,
        shelter_distance * 0.2
    ]

    fig, ax = plt.subplots()
    ax.bar(features, values)

    ax.set_ylabel("위험 기여 점수")
    ax.set_title("요인별 위험 기여도")

    st.pyplot(fig, use_container_width=True)

    st.success("✔ 체감온도가 가장 큰 영향 요인")
