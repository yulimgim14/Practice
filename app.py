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
            st.markdown(f"""<div class="info-card"><span style="font-size:13px;color:#60A5FA">{row.get('재활용품배출방법','정보없음')}</span></div>""", unsafe_allow_html=True)

            st.markdown("**🥡 음식물 쓰레기**")
            st.markdown(f"""<div class="info-card"><span style="font-size:13px;color:#FB923C">{row.get('음식물쓰레기배출방법','정보없음')}</span></div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"#### 🗓️ 배출 요일 & 시간")
        if not gu_info.empty:
            all_days = ["일", "월", "화", "수", "목", "금", "토"]

            for label, col_key in [("일반쓰레기", "생활쓰레기배출요일"), ("재활용", "재활용품배출요일"), ("음식물", "음식물쓰레기배출요일")]:
                days_str = gu_info.iloc[0].get(col_key, "")
                if pd.notna(days_str):
                    active = [d.strip() for d in str(days_str).split("+")]
                    badges = "".join([
                        f'<span class="day-badge {"day-on" if d in active else "day-off"}">{d}</span>'
                        for d in all_days
                    ])
                    st.markdown(f"**{label}**")
                    st.markdown(f'<div style="margin-bottom:10px">{badges}</div>', unsafe_allow_html=True)

            start = gu_info.iloc[0].get("생활쓰레기배출시작시각", "")
            end = gu_info.iloc[0].get("생활쓰레기배출종료시각", "")
            if pd.notna(start) and pd.notna(end):
                st.markdown(f"""
                <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:10px;padding:12px;margin-top:8px;">
                    <div style="color:#6B7280;font-size:11px;margin-bottom:4px">배출 가능 시간</div>
                    <div style="font-size:20px;font-weight:700;color:#4ADE98;font-family:'DM Mono',monospace">{start} ~ {end}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### 💰 종량제 봉투 가격")
        if not gu_price.empty:
            p_row = gu_price.iloc[0]
            sizes = ["10ℓ", "20ℓ", "30ℓ", "50ℓ"]
            cols_p = st.columns(4)
            for i, sz in enumerate(sizes):
                col_name = f"{sz}가격"
                if col_name in p_row and pd.notna(p_row[col_name]) and p_row[col_name] > 0:
                    cols_p[i].markdown(f"""
                    <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:8px;padding:10px;text-align:center">
                        <div style="color:#6B7280;font-size:11px">{sz}</div>
                        <div style="color:#4ADE98;font-size:16px;font-weight:700;font-family:'DM Mono',monospace">{int(p_row[col_name])}<span style="font-size:10px">원</span></div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 서울 25개 구 1인당 배출량 비교")
    rank_df2 = xl.sort_values("1인당배출량", ascending=True)
    colors = ["#4ADE98" if g == selected_gu else "#2A3A4A" for g in rank_df2["구"]]
    fig = go.Figure(go.Bar(
        x=rank_df2["1인당배출량"], y=rank_df2["구"],
        orientation="h",
        marker_color=colors,
        text=rank_df2["1인당배출량"].apply(lambda x: f"{x:.2f}"),
        textposition="outside",
        textfont=dict(size=10, color="#8A8A9A"),
    ))
    fig.update_layout(
        height=560,
        plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
        font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
        xaxis=dict(gridcolor="#1A1D2A", title="㎏/인·일", title_font=dict(color="#6B7280")),
        yaxis=dict(gridcolor="#1A1D2A"),
        margin=dict(l=80, r=60, t=20, b=40),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# 2. 배출량 분석
# ═══════════════════════════════════════════════════════════════════
elif menu == "📊 배출량 분석":
    st.markdown("### 📊 서울시 생활쓰레기 배출량 분석")

    tab1, tab2, tab3 = st.tabs(["🏆 구별 순위", "📈 분포 분석", "🔍 상관관계"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 1인당 배출량 TOP/BOTTOM 5")
            top5 = xl.nlargest(5, "1인당배출량")[["구", "1인당배출량"]]
            bot5 = xl.nsmallest(5, "1인당배출량")[["구", "1인당배출량"]]

            fig = make_subplots(rows=1, cols=2, subplot_titles=("상위 5구", "하위 5구"))
            fig.add_trace(go.Bar(
                x=top5["구"], y=top5["1인당배출량"],
                marker_color="#F87171", name="상위",
                text=top5["1인당배출량"].apply(lambda x: f"{x:.2f}"),
                textposition="outside", textfont=dict(size=10, color="#F87171"),
            ), row=1, col=1)
            fig.add_trace(go.Bar(
                x=bot5["구"], y=bot5["1인당배출량"],
                marker_color="#4ADE98", name="하위",
                text=bot5["1인당배출량"].apply(lambda x: f"{x:.2f}"),
                textposition="outside", textfont=dict(size=10, color="#4ADE98"),
            ), row=1, col=2)
            fig.update_layout(
                height=320, showlegend=False,
                plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
                font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
                margin=dict(l=20, r=20, t=40, b=40),
            )
            fig.update_xaxes(gridcolor="#1A1D2A")
            fig.update_yaxes(gridcolor="#1A1D2A")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 총 배출량 상위 10구")
            top10 = xl.nlargest(10, "총배출량").sort_values("총배출량")
            fig2 = go.Figure(go.Bar(
                x=top10["총배출량"], y=top10["구"],
                orientation="h",
                marker=dict(
                    color=top10["총배출량"],
                    colorscale=[[0, "#1A3A2A"], [0.5, "#2A6449"], [1, "#4ADE98"]],
                ),
                text=top10["총배출량"].apply(lambda x: f"{x:,.0f}t"),
                textposition="outside",
                textfont=dict(size=10, color="#8A8A9A"),
            ))
            fig2.update_layout(
                height=320,
                plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
                font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
                xaxis=dict(gridcolor="#1A1D2A", title="톤/일"),
                yaxis=dict(gridcolor="#1A1D2A"),
                margin=dict(l=80, r=80, t=20, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### 전체 자치구 배출량 현황")
        display_df = xl.copy().sort_values("1인당배출량", ascending=False).reset_index(drop=True)
        display_df.index += 1
        display_df.columns = ["자치구", "1인당 배출량 (㎏/인·일)", "총 배출량 (톤/일)", "인구 (명)"]
        display_df["1인당 배출량 (㎏/인·일)"] = display_df["1인당 배출량 (㎏/인·일)"].apply(lambda x: f"{x:.2f}")
        display_df["총 배출량 (톤/일)"] = display_df["총 배출량 (톤/일)"].apply(lambda x: f"{x:,.1f}")
        display_df["인구 (명)"] = display_df["인구 (명)"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(display_df, use_container_width=True, height=400)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 1인당 배출량 분포")
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=xl["1인당배출량"],
                nbinsx=12,
                marker_color="#4ADE98",
                opacity=0.8,
                name="분포",
            ))
            fig.add_vline(
                x=xl["1인당배출량"].mean(),
                line_dash="dash", line_color="#60A5FA",
                annotation_text=f"평균 {xl['1인당배출량'].mean():.2f}",
                annotation_font_color="#60A5FA",
            )
            fig.update_layout(
                height=300,
                plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
                font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
                xaxis=dict(gridcolor="#1A1D2A", title="㎏/인·일"),
                yaxis=dict(gridcolor="#1A1D2A", title="구 수"),
                margin=dict(l=40, r=20, t=20, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 배출량 vs 인구 버블차트")
            fig3 = go.Figure(go.Scatter(
                x=xl["인구수"],
                y=xl["1인당배출량"],
                mode="markers+text",
                marker=dict(
                    size=xl["총배출량"] / xl["총배출량"].max() * 60 + 10,
                    color=xl["1인당배출량"],
                    colorscale=[[0, "#1A3A2A"], [0.5, "#2A6449"], [1, "#F87171"]],
                    showscale=True,
                    colorbar=dict(title="㎏/인", tickfont=dict(color="#6B7280"), title_font=dict(color="#6B7280")),
                ),
                text=xl["구"],
                textposition="top center",
                textfont=dict(size=9, color="#8A8A9A"),
            ))
            fig3.update_layout(
                height=300,
                plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
                font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
                xaxis=dict(gridcolor="#1A1D2A", title="인구 (명)"),
                yaxis=dict(gridcolor="#1A1D2A", title="1인당 배출량"),
                margin=dict(l=40, r=20, t=20, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown("##### 총 배출량 vs 인구 상관관계")
        fig4 = px.scatter(
            xl, x="인구수", y="총배출량",
            text="구", trendline="ols",
            labels={"인구수": "인구 (명)", "총배출량": "총 배출량 (톤/일)"},
            color="1인당배출량",
            color_continuous_scale=[[0, "#1A3A2A"], [0.5, "#4ADE98"], [1, "#F87171"]],
        )
        fig4.update_traces(
            textposition="top center",
            textfont=dict(size=9, color="#8A8A9A"),
            marker_size=10,
        )
        fig4.update_layout(
            height=420,
            plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
            font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
            xaxis=dict(gridcolor="#1A1D2A"),
            yaxis=dict(gridcolor="#1A1D2A"),
            margin=dict(l=40, r=40, t=20, b=40),
            coloraxis_colorbar=dict(title="1인당 배출량", tickfont=dict(color="#6B7280"), title_font=dict(color="#6B7280")),
        )
        st.plotly_chart(fig4, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("평균 1인당 배출량", f"{xl['1인당배출량'].mean():.2f} ㎏")
        with col2:
            st.metric("최대 구", f"{xl.loc[xl['1인당배출량'].idxmax(),'구']} ({xl['1인당배출량'].max():.2f}㎏)")
        with col3:
            st.metric("최소 구", f"{xl.loc[xl['1인당배출량'].idxmin(),'구']} ({xl['1인당배출량'].min():.2f}㎏)")


# ═══════════════════════════════════════════════════════════════════
# 3. 배출 지도
# ═══════════════════════════════════════════════════════════════════
elif menu == "🗺️ 배출 지도":
    st.markdown("### 🗺️ 서울시 배출 현황 지도")

    map_type = st.selectbox("지도 표시 기준", ["1인당 배출량", "총 배출량", "배출 장소 유형"])

    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    if map_type in ["1인당 배출량", "총 배출량"]:
        col_key = "1인당배출량" if map_type == "1인당 배출량" else "총배출량"
        val_max = xl[col_key].max()
        val_min = xl[col_key].min()

        for _, row in xl.iterrows():
            gu_name = row["구"]
            coord = DISTRICT_COORDS.get(gu_name)
            if not coord:
                continue
            val = row[col_key]
            ratio = (val - val_min) / (val_max - val_min) if val_max != val_min else 0.5
            r = int(74 + (248 - 74) * ratio)
            g = int(222 - (222 - 113) * ratio)
            b = int(152 - (152 - 113) * ratio)
            color = f"#{r:02X}{g:02X}{b:02X}"

            unit = "㎏/인·일" if col_key == "1인당배출량" else "톤/일"
            popup_html = f"""
            <div style="font-family:sans-serif;min-width:160px;background:#1A1D2A;color:#E8E8E0;
                        padding:10px;border-radius:8px;border:1px solid #2A2D3A">
                <b style="color:#4ADE98;font-size:14px">{gu_name}</b><br>
                <span style="color:#A0A0B0;font-size:12px">{map_type}: <b style="color:#E8E8E0">{val:.2f} {unit}</b></span><br>
                <span style="color:#A0A0B0;font-size:11px">인구: {row['인구수']:,.0f}명</span>
            </div>
            """
            folium.CircleMarker(
                location=coord,
                radius=12 + ratio * 20,
                color=color, fill=True, fill_color=color,
                fill_opacity=0.75, weight=2,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"{gu_name}: {val:.2f} {unit}",
            ).add_to(m)

    else:
        type_colors = {"문전수거": "#4ADE98", "거점수거": "#60A5FA", "기타": "#FB923C"}
        for gu_name, coord in DISTRICT_COORDS.items():
            gu_i = info[info["시군구명"] == gu_name]
            if gu_i.empty:
                continue
            btype = gu_i.iloc[0].get("배출장소유형", "기타")
            color = type_colors.get(btype, "#8B8B9B")
            popup_html = f"""
            <div style="font-family:sans-serif;min-width:140px;background:#1A1D2A;color:#E8E8E0;
                        padding:10px;border-radius:8px;border:1px solid #2A2D3A">
                <b style="color:#4ADE98;font-size:14px">{gu_name}</b><br>
                <span style="font-size:12px;color:{color}">● {btype}</span>
            </div>
            """
            folium.CircleMarker(
                location=coord,
                radius=14,
                color=color, fill=True, fill_color=color,
                fill_opacity=0.8, weight=2,
                popup=folium.Popup(popup_html, max_width=180),
                tooltip=f"{gu_name}: {btype}",
            ).add_to(m)

        legend_html = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                    background:#1A1D2A;border:1px solid #2A2D3A;border-radius:10px;padding:12px;font-family:sans-serif">
            <div style="color:#E8E8E0;font-size:12px;font-weight:700;margin-bottom:6px">배출 유형</div>
            <div style="color:#4ADE98;font-size:11px">● 문전수거</div>
            <div style="color:#60A5FA;font-size:11px">● 거점수거</div>
            <div style="color:#FB923C;font-size:11px">● 기타</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

    if selected_gu in DISTRICT_COORDS:
        coord = DISTRICT_COORDS[selected_gu]
        folium.Marker(
            location=coord,
            popup=f"📍 {selected_gu} (선택됨)",
            icon=folium.Icon(color="green", icon="star", prefix="fa"),
        ).add_to(m)

    st_folium(m, height=520, use_container_width=True)

    st.markdown(f"#### 📍 {selected_gu} 배출 장소 상세")
    if not gu_info.empty:
        for _, row in gu_info.iterrows():
            btype = row.get("배출장소유형", "")
            bplace = row.get("배출장소", "")
            col_badge = "badge-green" if btype == "문전수거" else "badge-blue" if btype == "거점수거" else "badge-orange"
            st.markdown(f"""
            <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:10px;padding:12px;margin:4px 0">
                <span class="badge {col_badge}">{btype}</span>
                <span style="font-size:13px;color:#C0C0D0;margin-left:8px">{bplace}</span>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 4. 종량제 가격표
# ═══════════════════════════════════════════════════════════════════
elif menu == "💰 종량제 가격표":
    st.markdown("### 💰 서울시 종량제 봉투 가격표")

    tab1, tab2 = st.tabs(["📋 구별 가격 비교", "🔍 내 동네 가격"])

    with tab1:
        filter_type = st.selectbox("봉투 용도", ["생활쓰레기", "음식물쓰레기"])
        filter_kind = st.selectbox("봉투 종류", ["규격봉투", "재사용규격봉투", "특수규격마대"])

        price_filtered = seoul_price[
            (seoul_price["종량제봉투용도"] == filter_type) &
            (seoul_price["종량제봉투종류"] == filter_kind) &
            (seoul_price["종량제봉투사용대상"] == "가정용")
        ][["시군구명", "10ℓ가격", "20ℓ가격", "30ℓ가격", "50ℓ가격"]].drop_duplicates("시군구명")

        size_cols = ["10ℓ가격", "20ℓ가격", "30ℓ가격", "50ℓ가격"]
        selected_size = st.selectbox("비교 용량", ["10ℓ", "20ℓ", "30ℓ", "50ℓ"], index=1)
        size_col = f"{selected_size}가격"

        plot_df = price_filtered[price_filtered[size_col] > 0].sort_values(size_col, ascending=True)
        if not plot_df.empty:
            colors = ["#4ADE98" if g == selected_gu else "#2A3A4A" for g in plot_df["시군구명"]]
            fig = go.Figure(go.Bar(
                x=plot_df[size_col], y=plot_df["시군구명"],
                orientation="h",
                marker_color=colors,
                text=plot_df[size_col].apply(lambda x: f"{int(x)}원"),
                textposition="outside",
                textfont=dict(size=10, color="#8A8A9A"),
            ))
            fig.update_layout(
                height=480,
                plot_bgcolor="#0F1117", paper_bgcolor="#0F1117",
                font=dict(family="Noto Sans KR", color="#A0A0B0", size=11),
                xaxis=dict(gridcolor="#1A1D2A", title="가격 (원)"),
                yaxis=dict(gridcolor="#1A1D2A"),
                margin=dict(l=80, r=80, t=20, b=40),
                showlegend=False,
                title=dict(text=f"{filter_type} {filter_kind} {selected_size} 가격 비교", font=dict(color="#C0C0D0", size=14)),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("해당 조건의 가격 데이터가 없습니다.")

        st.markdown("##### 전체 가격표")
        display_price = price_filtered.copy()
        for c in size_cols:
            display_price[c] = display_price[c].apply(lambda x: f"{int(x)}원" if pd.notna(x) and x > 0 else "-")
        display_price.columns = ["자치구", "10ℓ", "20ℓ", "30ℓ", "50ℓ"]
        st.dataframe(display_price.set_index("자치구"), use_container_width=True)

    with tab2:
        st.markdown(f"#### {selected_gu} 봉투 가격 상세")
        for usage in ["생활쓰레기", "음식물쓰레기"]:
            st.markdown(f"**{usage}**")
            p_df = seoul_price[
                (seoul_price["시군구명"] == selected_gu) &
                (seoul_price["종량제봉투용도"] == usage)
            ]
            if p_df.empty:
                st.markdown('<div class="warn-card">데이터 없음</div>', unsafe_allow_html=True)
                continue

            for _, row in p_df.iterrows():
                kind = row.get("종량제봉투종류", "")
                target = row.get("종량제봉투사용대상", "")

                size_prices = []
                for sz in ["1ℓ", "2ℓ", "3ℓ", "5ℓ", "10ℓ", "20ℓ", "30ℓ", "50ℓ", "75ℓ", "100ℓ"]:
                    col = f"{sz}가격"
                    if col in row and pd.notna(row[col]) and row[col] > 0:
                        size_prices.append((sz, int(row[col])))

                if not size_prices:
                    continue

                prices_html = "".join([
                    f'<div style="background:#0F1117;border-radius:6px;padding:8px;text-align:center">'
                    f'<div style="color:#6B7280;font-size:10px">{sz}</div>'
                    f'<div style="color:#4ADE98;font-size:14px;font-weight:700;font-family:\'DM Mono\',monospace">{p:,}<span style="font-size:9px">원</span></div>'
                    f'</div>'
                    for sz, p in size_prices
                ])
                st.markdown(f"""
                <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:10px;padding:12px;margin:6px 0">
                    <div style="margin-bottom:10px">
                        <span class="badge badge-blue">{kind}</span>
                        <span class="badge badge-green">{target}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(70px,1fr));gap:6px">
                        {prices_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 5. 배출 일정
# ═══════════════════════════════════════════════════════════════════
elif menu == "📅 배출 일정":
    st.markdown(f"### 📅 {selected_gu} 배출 일정 안내")

    if gu_info.empty:
        st.warning("선택한 구의 배출 정보가 없습니다.")
    else:
        categories = [
            ("🗑️ 일반쓰레기", "생활쓰레기배출요일", "생활쓰레기배출시작시각", "생활쓰레기배출종료시각", "badge-orange"),
            ("♻️ 재활용", "재활용품배출요일", "재활용품배출시작시각", "재활용품배출종료시각", "badge-blue"),
            ("🥡 음식물", "음식물쓰레기배출요일", "음식물쓰레기배출시작시각", "음식물쓰레기배출종료시각", "badge-green"),
        ]

        st.markdown("##### 🗓️ 주간 배출 일정표")
        week_data = {d: [] for d in ["월", "화", "수", "목", "금", "토", "일"]}

        for label, day_col, start_col, end_col, badge_cls in categories:
            for _, row in gu_info.iterrows():
                days_str = row.get(day_col, "")
                if pd.isna(days_str):
                    continue
                active_days = [d.strip() for d in str(days_str).split("+")]
                for d in active_days:
                    if d in week_data:
                        week_data[d].append(label)

        day_cols = st.columns(7)
        day_labels = ["월", "화", "수", "목", "금", "토", "일"]
        import datetime
        today_weekday = datetime.datetime.now().weekday()
        today_kr = day_labels[today_weekday]

        for i, (day, col) in enumerate(zip(day_labels, day_cols)):
            is_today = (day == today_kr)
            items = list(dict.fromkeys(week_data.get(day, [])))
            border = "2px solid #4ADE98" if is_today else "1px solid #2A2D3A"
            bg = "#1A2A20" if is_today else "#1A1D2A"
            today_badge = '<div style="color:#4ADE98;font-size:9px;font-weight:700;margin-bottom:4px">TODAY</div>' if is_today else ""
            items_html = "".join([f'<div style="font-size:9px;color:#A0C0B0;padding:2px 0">{it}</div>' for it in items]) if items else '<div style="font-size:9px;color:#3A3D4A">없음</div>'
            col.markdown(f"""
            <div style="background:{bg};border:{border};border-radius:10px;padding:10px;text-align:center;min-height:100px">
                {today_badge}
                <div style="font-size:14px;font-weight:700;color:{'#4ADE98' if is_today else '#C0C0D0'};margin-bottom:6px">{day}</div>
                {items_html}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        for label, day_col, start_col, end_col, badge_cls in categories:
            st.markdown(f"#### {label}")
            for idx, row in gu_info.iterrows():
                days_str = row.get(day_col, "")
                start = row.get(start_col, "")
                end = row.get(end_col, "")
                bplace = row.get("배출장소", "")

                if pd.isna(days_str):
                    continue
                active_days = [d.strip() for d in str(days_str).split("+")]
                all_7 = ["일", "월", "화", "수", "목", "금", "토"]
                day_badges = "".join([
                    f'<span class="day-badge {"day-on" if d in active_days else "day-off"}">{d}</span>'
                    for d in all_7
                ])
                time_info = f"{start} ~ {end}" if pd.notna(start) and pd.notna(end) else "시간 미지정"
                place_info = bplace if pd.notna(bplace) else ""

                st.markdown(f"""
                <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:12px;padding:14px;margin:6px 0">
                    <div style="margin-bottom:8px">{day_badges}</div>
                    <div style="display:flex;gap:16px;flex-wrap:wrap">
                        <div>
                            <span style="color:#6B7280;font-size:11px">배출 시간</span><br>
                            <span style="color:#4ADE98;font-size:14px;font-weight:700;font-family:'DM Mono',monospace">{time_info}</span>
                        </div>
                        {f'<div><span style="color:#6B7280;font-size:11px">배출 장소</span><br><span style="color:#C0C0D0;font-size:12px">{place_info}</span></div>' if place_info else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💡 올바른 분리배출 가이드")
    tips = [
        ("🗑️", "일반쓰레기", "종량제 봉투에 넣어 배출. 음식물, 재활용품은 반드시 분리 후 배출"),
        ("♻️", "종이류", "신문지·박스는 묶어서, 비닐 코팅된 종이는 일반쓰레기로"),
        ("🥡", "음식물", "물기를 최대한 제거 후 전용 봉투에. 이물질·비닐 혼입 금지"),
        ("📦", "플라스틱", "내용물 비우고 헹궈서 투명 봉투에. 라벨 제거 후 배출"),
        ("🔋", "형광등·건전지", "주민센터·마트 수거함 이용. 일반쓰레기 절대 금지"),
        ("🛋️", "대형폐기물", "배출 전 인터넷·전화로 스티커 구매 필수 (구청 문의)"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(tips):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1A1D2A;border:1px solid #2A2D3A;border-radius:10px;padding:14px;margin:4px 0">
                <div style="font-size:20px;margin-bottom:6px">{icon}</div>
                <div style="font-size:13px;font-weight:700;color:#C0C0D0;margin-bottom:4px">{title}</div>
                <div style="font-size:12px;color:#6B7280;line-height:1.5">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
