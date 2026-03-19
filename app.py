import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="폭염 취약성 분석 앱", layout="wide")

st.title("🔥 폭염 취약성 & 온열질환 위험 예측")

# -------------------------
# 입력
# -------------------------
st.sidebar.header("📊 입력 변수")

temp = st.sidebar.slider("일 최고기온 (°C)", 25, 45, 33)
heat_index = st.sidebar.slider("체감온도 (°C)", 25, 45, 35)
elderly_ratio = st.sidebar.slider("노인 인구 비율 (%)", 0, 50, 20)
living_alone_ratio = st.sidebar.slider("독거노인 비율 (%)", 0, 50, 15)
shelter_distance = st.sidebar.slider("쉼터 평균 접근 시간 (분)", 1, 30, 10)

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

# 위험 등급
if risk_score < 30:
    risk_level = "🟢 낮음"
elif risk_score < 50:
    risk_level = "🟡 중간"
else:
    risk_level = "🔴 높음"

# -------------------------
# 정책 추천
# -------------------------
policy = []

if shelter_distance > 15:
    policy.append("🏠 마이크로 쉼터 확대")

if living_alone_ratio > 20:
    policy.append("👵 방문 케어 강화")

if heat_index >= 35:
    policy.append("🚨 폭염 대응체계 가동")

if not policy:
    policy.append("✅ 유지")

# -------------------------
# 결과
# -------------------------
st.subheader("📈 분석 결과")

col1, col2 = st.columns(2)

with col1:
    st.metric("위험 점수", round(risk_score, 2))
    st.metric("위험 등급", risk_level)

with col2:
    st.markdown("### 📌 정책 추천")
    for p in policy:
        st.write("-", p)

# =========================
# 📊 시각화 추가
# =========================

st.markdown("---")
st.subheader("📊 데이터 시각화")

# 1️⃣ 체감온도 vs 위험도
temps = np.arange(25, 46)
risk_curve = []

for t in temps:
    score = (t * 0.4) + (elderly_ratio * 0.2) + (living_alone_ratio * 0.2) + (shelter_distance * 0.2)
    if t >= 35:
        score *= 1.3
    risk_curve.append(score)

fig1, ax1 = plt.subplots()
ax1.plot(temps, risk_curve)
ax1.axvline(x=35, linestyle='--')  # 임계점
ax1.set_title("체감온도 vs 위험도")
ax1.set_xlabel("체감온도")
ax1.set_ylabel("위험 점수")

st.pyplot(fig1)

# 2️⃣ 쉼터 거리 vs 위험도
distances = np.arange(1, 31)
risk_dist = []

for d in distances:
    score = (heat_index * 0.4) + (elderly_ratio * 0.2) + (living_alone_ratio * 0.2) + (d * 0.2)
    if heat_index >= 35:
        score *= 1.3
    risk_dist.append(score)

fig2, ax2 = plt.subplots()
ax2.plot(distances, risk_dist)
ax2.set_title("쉼터 접근 시간 vs 위험도")
ax2.set_xlabel("거리 (분)")
ax2.set_ylabel("위험 점수")

st.pyplot(fig2)

# 3️⃣ 변수 영향도 (bar chart)
features = ["체감온도", "노인비율", "독거노인", "쉼터거리"]
values = [
    heat_index * 0.4,
    elderly_ratio * 0.2,
    living_alone_ratio * 0.2,
    shelter_distance * 0.2
]

fig3, ax3 = plt.subplots()
ax3.bar(features, values)
ax3.set_title("위험도 기여도")

st.pyplot(fig3)
