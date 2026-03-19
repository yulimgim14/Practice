
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="폭염 취약성 분석 앱", layout="wide")

st.title("🔥 폭염 취약성 & 온열질환 위험 예측")
st.markdown("간단한 변수 입력으로 지역의 온열질환 위험도와 정책을 추천합니다.")

# -------------------------
# 사용자 입력
# -------------------------
st.sidebar.header("📊 입력 변수")

temp = st.sidebar.slider("일 최고기온 (°C)", 25, 45, 33)
heat_index = st.sidebar.slider("체감온도 (°C)", 25, 45, 35)
elderly_ratio = st.sidebar.slider("노인 인구 비율 (%)", 0, 50, 20)
living_alone_ratio = st.sidebar.slider("독거노인 비율 (%)", 0, 50, 15)
shelter_distance = st.sidebar.slider("쉼터 평균 접근 시간 (분)", 1, 30, 10)

# -------------------------
# 위험도 계산 (간단 모델)
# -------------------------
risk_score = (
    (heat_index * 0.4) +
    (elderly_ratio * 0.2) +
    (living_alone_ratio * 0.2) +
    (shelter_distance * 0.2)
)

# 임계점 반영
if heat_index >= 35:
    risk_score *= 1.3

# -------------------------
# 위험 등급 분류
# -------------------------
if risk_score < 30:
    risk_level = "🟢 낮음"
elif risk_score < 50:
    risk_level = "🟡 중간"
else:
    risk_level = "🔴 높음"

# -------------------------
# 정책 추천 로직
# -------------------------
policy = []

if shelter_distance > 15:
    policy.append("🏠 마이크로 무더위 쉼터 확대 필요")

if living_alone_ratio > 20:
    policy.append("👵 독거노인 방문 케어 강화 필요")

if heat_index >= 35:
    policy.append("🚨 폭염 경보 대응체계 즉시 가동")

if elderly_ratio > 25:
    policy.append("💊 고령층 맞춤 건강 모니터링 필요")

if not policy:
    policy.append("✅ 현재 상태 유지 및 모니터링")

# -------------------------
# 결과 출력
# -------------------------
st.subheader("📈 분석 결과")

col1, col2 = st.columns(2)

with col1:
    st.metric("🔥 위험 점수", round(risk_score, 2))
    st.metric("⚠️ 위험 등급", risk_level)

with col2:
    st.markdown("### 📌 정책 추천")
    for p in policy:
        st.write("-", p)

# -------------------------
# 인사이트 설명
# -------------------------
st.markdown("---")
st.markdown("### 🧠 해석")

if heat_index >= 35:
    st.warning("체감온도 35도 이상 → 온열질환 급증 임계 구간")

if shelter_distance > 15:
    st.warning("쉼터 접근성 부족 → 정책 실효성 낮음")

if living_alone_ratio > 20:
    st.warning("독거노인 비율 높음 → 응급 대응 취약")

st.success("데이터 기반 정책 설계가 필요합니다.")
