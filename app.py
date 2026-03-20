import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import numpy as np

# ── 페이지 설정 ───────────────────────────────────────────────────
st.set_page_config(
    page_title="서울 스마트 분리배출 도우미",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 전역 CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 */
.stApp {
    background: #0F1117;
    color: #E8E8E0;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #161820 !important;
    border-right: 1px solid #2A2D3A;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    color: #A0A0B0 !important;
}

/* 메트릭 카드 */
[data-testid="metric-container"] {
    background: #1A1D2A;
    border: 1px solid #2A2D3A;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="stMetricValue"] {
    color: #4ADE98 !important;
    font-family: 'DM Mono', monospace;
}
[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-size: 12px !important;
}
[data-testid="stMetricDelta"] {
    color: #60A5FA !important;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    background: #161820;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #2A2D3A;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #6B7280;
    font-weight: 500;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #2A6449 !important;
    color: #4ADE98 !important;
}

/* 데이터프레임 */
.stDataFrame {
    border: 1px solid #2A2D3A !important;
    border-radius: 12px;
}

/* 헤더 */
h1 { color: #E8E8E0 !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2 { color: #C8C8C0 !important; font-weight: 500 !important; }
h3 { color: #A8A8A0 !important; font-weight: 500 !important; }

/* selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1A1D2A;
    border: 1px solid #2A2D3A;
    border-radius: 8px;
    color: #E8E8E0;
}

/* 구분선 */
hr { border-color: #2A2D3A !important; }

/* expander */
[data-testid="stExpander"] {
    background: #1A1D2A;
    border: 1px solid #2A2D3A;
    border-radius: 12px;
}

/* info/warning box */
.info-card {
    background: #1A2A20;
    border: 1px solid #2A6449;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}
.warn-card {
    background: #2A1F10;
    border: 1px solid #8B6914;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* 배지 */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    margin: 2px;
}
.badge-green { background: #162A20; color: #4ADE98; border: 1px solid #2A6449; }
.badge-blue { background: #162030; color: #60A5FA; border: 1px solid #1D4ED8; }
.badge-orange { background: #2A1A0A; color: #FB923C; border: 1px solid #9A4E1A; }
.badge-red { background: #2A1010; color: #F87171; border: 1px solid #9A1A1A; }

/* 구 선택 카드 */
.district-card {
    background: #1A1D2A;
    border: 1px solid #2A2D3A;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
}

/* 타이틀 스타일 */
.app-title {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #4ADE98, #34D399, #60A5FA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.app-subtitle {
    color: #6B7280;
    font-size: 14px;
    margin-bottom: 24px;
}

/* 섹션 헤더 */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 16px;
}

/* 요일 뱃지 */
.day-badge {
    display: inline-block;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}
.day-on { background: #2A6449; color: #4ADE98; }
.day-off { background: #1A1D2A; color: #3A3D4A; }

.stButton > button {
    background: #1A2A20 !important;
    color: #4ADE98 !important;
    border: 1px solid #2A6449 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background: #2A6449 !important;
    border-color: #4ADE98 !important;
}
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    # 서울 배출량
    xl = pd.read_excel("서울시배출량.xlsx")
    xl.columns = ["구", "1인당배출량", "총배출량", "인구수"]
    xl = xl.iloc[2:].copy()  # 헤더행, 합계행 제거
    xl["1인당배출량"] = pd.to_numeric(xl["1인당배출량"], errors="coerce")
    xl["총배출량"] = pd.to_numeric(xl["총배출량"], errors="coerce")
    xl["인구수"] = pd.to_numeric(xl["인구수"], errors="coerce")
    xl = xl.dropna()

    # 서울 배출정보
    info = pd.read_csv("생활쓰레기배출정보_서울특별시.csv", encoding="cp949")

    # 종량제 가격
    price = pd.read_csv("전국종량제봉투가격표준데이터.csv", encoding="cp949")
    seoul_price = price[price["시도명"] == "서울특별시"].copy()

    return xl, info, seoul_price


xl, info, seoul_price = load_data()

# 서울 자치구 중심 좌표
DISTRICT_COORDS = {
    "종로구": [37.5730, 126.9794], "중구": [37.5638, 126.9979], "용산구": [37.5311, 126.9810],
    "성동구": [37.5636, 127.0369], "광진구": [37.5384, 127.0822], "동대문구": [37.5744, 127.0395],
    "중랑구": [37.5965, 127.0927], "성북구": [37.5894, 127.0167], "강북구": [37.6396, 127.0254],
    "도봉구": [37.6688, 127.0474], "노원구": [37.6543, 127.0569], "은평구": [37.6026, 126.9291],
    "서대문구": [37.5791, 126.9368], "마포구": [37.5665, 126.9011], "양천구": [37.5170, 126.8666],
    "강서구": [37.5509, 126.8496], "구로구": [37.4954, 126.8874], "금천구": [37.4569, 126.8955],
    "영등포구": [37.5263, 126.8964], "동작구": [37.5124, 126.9393], "관악구": [37.4784, 126.9516],
    "서초구": [37.4836, 127.0327], "강남구": [37.5172, 127.0473], "송파구": [37.5145, 127.1058],
    "강동구": [37.5301, 127.1237],
}

# ── 사이드바 ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 24px;">
        <div style="font-size: 36px; margin-bottom: 8px;">♻️</div>
        <div style="font-size: 16px; font-weight: 700; color: #4ADE98;">스마트 분리배출</div>
        <div style="font-size: 11px; color: #6B7280; margin-top: 4px;">서울시 생활쓰레기 종합 가이드</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏙️ 자치구 선택")
    all_districts = sorted(xl["구"].tolist())
    selected_gu = st.selectbox("분석할 자치구", all_districts, index=all_districts.index("강남구") if "강남구" in all_districts else 0)

    st.markdown("---")
    st.markdown("### 📋 메뉴")
    menu = st.radio(
        "",
        ["🏠 대시보드", "📊 배출량 분석", "🗺️ 배출 지도", "💰 종량제 가격표", "📅 배출 일정"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: #3A3D4A; text-align: center; padding: 8px 0;">
        데이터 출처: 공공데이터포털<br>
        서울 열린데이터광장 2024
    </div>
    """, unsafe_allow_html=True)


# ── 헤더 ──────────────────────────────────────────────────────────
st.markdown("""
<div class="app-title">♻ 서울 스마트 분리배출 도우미</div>
<div class="app-subtitle">서울시 25개 자치구 생활쓰레기 배출 정보 · 배출량 통계 · 종량제 가격 통합 플랫폼</div>
""", unsafe_allow_html=True)


# ── 선택된 구 데이터 ────────────────────────────────────────────────
gu_xl = xl[xl["구"] == selected_gu].iloc[0] if not xl[xl["구"] == selected_gu].empty else None
gu_info = info[info["시군구명"] == selected_gu]
gu_price = seoul_price[
    (seoul_price["시군구명"] == selected_gu) &
    (seoul_price["종량제봉투용도"] == "생활쓰레기") &
    (seoul_price["종량제봉투종류"] == "규격봉투") &
    (seoul_price["종량제봉투사용대상"] == "가정용")
]


# ═══════════════════════════════════════════════════════════════════
# 1. 대시보드
# ═══════════════════════════════════════════════════════════════════
if menu == "🏠 대시보드":
    # 상단 메트릭
    col1, col2, col3, col4 = st.columns(4)

    total_avg = xl["1인당배출량"].mean()
    rank_df = xl.sort_values("1인당배출량", ascending=False).reset_index(drop=True)
    rank = rank_df[rank_df["구"] == selected_gu].index[0] + 1 if not rank_df[rank_df["구"] == selected_gu].empty else "-"

    with col1:
        if gu_xl is not None:
            delta = f"전체 평균 대비 {gu_xl['1인당배출량'] - total_avg:+.2f}㎏"
            st.metric("1인당 배출량", f"{gu_xl['1인당배출량']:.2f} ㎏/인·일", delta)
    with col2:
        if gu_xl is not None:
            st.metric("총 배출량", f"{gu_xl['총배출량']:,.0f} 톤/일", f"서울시 {rank}위")
    with col3:
        if gu_xl is not None:
            st.metric("인구", f"{gu_xl['인구수']:,.0f} 명")
    with col4:
        p20 = gu_price["20ℓ가격"].values[0] if not gu_price.empty else "-"
        st.metric("20ℓ 봉투가격", f"{p20}원" if p20 != "-" else "-", "가정용 기준")

    st.markdown("---")

    # 주요 배출 정보 카드
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown(f"#### 📍 {selected_gu} 배출 안내")
        if not gu_info.empty:
            row = gu_info.iloc[0]

            st.markdown("**🗑️ 일반 쓰레기**")
            st.markdown(f"""<div class="info-card"><span style="font-size:13px;color:#A0FFC0">{row.get('생활쓰레기배출방법','정보없음')}</span></div>""", unsafe_allow_html=True)

            st.markdown("**♻️ 재활용품**")
            st
