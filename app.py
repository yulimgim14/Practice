import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import numpy as np
import datetime

# ════════════════════════════════════════════════════════
#  페이지 설정
# ════════════════════════════════════════════════════════
st.set_page_config(
    page_title="스마트 분리배출 도우미",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════
#  전역 스타일  (라이트 테마 · 고가독성)
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

/* ══ 폰트 전역 ══ */
*, html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }

/* ══ 전체 앱 배경 & 기본 텍스트 — 다크모드 덮어쓰기 ══ */
.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"] {
    background-color: #F4F6F9 !important;
    color: #1E293B !important;
}

/* 메인 콘텐츠 영역 */
.block-container {
    padding-top: 0 !important;
    background-color: #F4F6F9 !important;
}

/* 기본 p, span, div 텍스트 */
p, span, div, label, li {
    color: #1E293B;
}

/* ══ 탭 ══ */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-bottom: 2px solid #E2E8F0 !important;
    padding: 0 28px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 14px 28px !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #166534 !important;
    border-bottom: 3px solid #16A34A !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #F4F6F9 !important;
    padding: 0 !important;
}

/* ══ 셀렉트박스 ══ */
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #1E293B !important;
    font-size: 14px !important;
}
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] p {
    color: #1E293B !important;
}

/* ══ 라디오 ══ */
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stRadio"] span {
    color: #374151 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ══ 메트릭 카드 ══ */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricValue"] {
    color: #15803D !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] {
    color: #2563EB !important;
    font-size: 12px !important;
}

/* ══ 데이터프레임 ══ */
[data-testid="stDataFrame"] {
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}
[data-testid="stDataFrame"] * {
    color: #1E293B !important;
    background-color: #FFFFFF !important;
}

/* ══ hr ══ */
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }

/* ══ 버튼 ══ */
.stButton > button {
    background: #FFFFFF !important;
    color: #15803D !important;
    border: 1.5px solid #86EFAC !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stButton > button:hover {
    background: #F0FDF4 !important;
    border-color: #16A34A !important;
}

/* ══ 커스텀 컴포넌트 ══ */

.app-header {
    background: linear-gradient(135deg, #15803D 0%, #0F5C41 40%, #0369A1 100%);
    padding: 22px 36px 18px;
    margin: -1rem -1rem 0;
}
.app-title { font-size: 23px; font-weight: 900; color: #FFFFFF !important; letter-spacing: -0.5px; }
.app-sub   { color: rgba(255,255,255,0.80) !important; font-size: 13px; margin-top: 4px; }

.card {
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-title {
    font-size: 11px; font-weight: 700; color: #94A3B8 !important;
    text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px;
}

.info-pill {
    display: inline-block; padding: 4px 13px; border-radius: 20px;
    font-size: 12px; font-weight: 600; margin: 2px;
}
.pill-green { background: #DCFCE7 !important; color: #15803D !important; border: 1.5px solid #86EFAC; }
.pill-blue  { background: #DBEAFE !important; color: #1D4ED8 !important; border: 1.5px solid #93C5FD; }
.pill-amber { background: #FEF3C7 !important; color: #92400E !important; border: 1.5px solid #FCD34D; }
.pill-red   { background: #FEE2E2 !important; color: #991B1B !important; border: 1.5px solid #FCA5A5; }
.pill-gray  { background: #F1F5F9 !important; color: #475569 !important; border: 1.5px solid #CBD5E1; }

.day-dot {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 50%;
    font-size: 12px; font-weight: 700; margin: 2px;
}
.dot-on  { background: #16A34A !important; color: #FFFFFF !important; box-shadow: 0 2px 6px rgba(22,163,74,0.4); }
.dot-off { background: #F1F5F9 !important; color: #94A3B8 !important; border: 1.5px solid #E2E8F0; }

.section-label {
    font-size: 11px; font-weight: 700; color: #94A3B8 !important;
    text-transform: uppercase; letter-spacing: 1.4px; margin: 20px 0 10px;
    display: block;
}

.price-cell {
    background: #F8FAFC !important;
    border: 1.5px solid #E2E8F0; border-radius: 10px;
    padding: 12px 8px; text-align: center;
}
.price-size { font-size: 11px; color: #64748B !important; font-weight: 600; margin-bottom: 5px; }
.price-val  { font-size: 18px; font-weight: 700; color: #15803D !important; font-family: 'JetBrains Mono', monospace; }
.price-won  { font-size: 11px; color: #94A3B8 !important; margin-top: 1px; }

.countdown-box {
    background: linear-gradient(135deg, #F0FDF4, #EFF6FF) !important;
    border: 1.5px solid #86EFAC; border-radius: 14px;
    padding: 16px 20px; text-align: center;
}
.countdown-label { font-size: 11px; color: #64748B !important; font-weight: 600; margin-bottom: 6px; }
.countdown-time  {
    font-size: 30px; font-weight: 900; color: #15803D !important;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 3px;
}
.countdown-note { font-size: 12px; color: #16A34A !important; margin-top: 5px; }

.rank-row {
    display: flex; align-items: center;
    padding: 8px 10px; border-radius: 8px; margin: 2px 0; font-size: 13px;
}
.rank-row:hover { background: #F0FDF4 !important; }
.rank-num { width: 28px; font-size: 11px; color: #CBD5E1 !important; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.rank-gu  { flex: 1; color: #1E293B !important; font-weight: 500; }
.rank-bar-wrap { width: 110px; height: 7px; background: #E2E8F0; border-radius: 4px; margin: 0 10px; }
.rank-bar { height: 100%; border-radius: 4px; }
.rank-val { width: 56px; text-align: right; color: #15803D !important; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  데이터 로드 & 가공
# ════════════════════════════════════════════════════════
@st.cache_data
def load_all():
    # ─ 배출량
    raw = pd.read_excel("서울시배출량.xlsx")
    raw.columns = ["구", "1인당", "총량", "인구"]
    raw = raw.iloc[2:].copy()
    raw["1인당"] = pd.to_numeric(raw["1인당"], errors="coerce")
    raw["총량"]  = pd.to_numeric(raw["총량"],  errors="coerce")
    raw["인구"]  = pd.to_numeric(raw["인구"],  errors="coerce")
    xl = raw.dropna().reset_index(drop=True)

    # ─ 배출 정보
    info = pd.read_csv("생활쓰레기배출정보_서울특별시.csv", encoding="cp949")

    # ─ 가격
    price_raw = pd.read_csv("전국종량제봉투가격표준데이터.csv", encoding="cp949")
    price = price_raw[price_raw["시도명"] == "서울특별시"].copy()

    return xl, info, price

xl, info, price = load_all()

# 구별 대표 행 (첫 번째)
info_rep = info.drop_duplicates("시군구명", keep="first").set_index("시군구명")

# 자치구 좌표
GU_COORD = {
    "종로구":[37.5730,126.9794], "중구":[37.5638,126.9979], "용산구":[37.5311,126.9810],
    "성동구":[37.5636,127.0369], "광진구":[37.5384,127.0822], "동대문구":[37.5744,127.0395],
    "중랑구":[37.5965,127.0927], "성북구":[37.5894,127.0167], "강북구":[37.6396,127.0254],
    "도봉구":[37.6688,127.0474], "노원구":[37.6543,127.0569], "은평구":[37.6026,126.9291],
    "서대문구":[37.5791,126.9368], "마포구":[37.5665,126.9011], "양천구":[37.5170,126.8666],
    "강서구":[37.5509,126.8496], "구로구":[37.4954,126.8874], "금천구":[37.4569,126.8955],
    "영등포구":[37.5263,126.8964], "동작구":[37.5124,126.9393], "관악구":[37.4784,126.9516],
    "서초구":[37.4836,127.0327], "강남구":[37.5172,127.0473], "송파구":[37.5145,127.1058],
    "강동구":[37.5301,127.1237],
}

ALL_GU = sorted(xl["구"].tolist())


# ════════════════════════════════════════════════════════
#  헤더
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
  <div class="app-title">♻ 스마트 분리배출 도우미</div>
  <div class="app-sub">서울시 25개 자치구 · 생활쓰레기 배출 정보 · 배출량 히트맵 · 종량제 봉투 가격 통합 플랫폼</div>
</div>
<div style="height:1px;background:#E8ECF0;margin-bottom:0"></div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  3개 탭
# ════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "  📍  배출 위치 & 일정  ",
    "  🔥  배출량 히트맵  ",
    "  💰  종량제 봉투 가격  ",
])


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 1 ─ 배출 위치 & 일정                            ║
# ╚══════════════════════════════════════════════════════╝
with tab1:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_sel, col_spacer = st.columns([2, 3])
    with col_sel:
        gu = st.selectbox("🏙️ 자치구 선택", ALL_GU,
                          index=ALL_GU.index("강남구") if "강남구" in ALL_GU else 0,
                          key="gu_tab1")

    gu_rows = info[info["시군구명"] == gu]

    # ── 상단 KPI
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    kc1, kc2, kc3, kc4 = st.columns(4)

    gu_xl = xl[xl["구"] == gu]
    avg_val = xl["1인당"].mean()
    if not gu_xl.empty:
        v1 = float(gu_xl["1인당"].values[0])
        v2 = float(gu_xl["총량"].values[0])
        v3 = int(gu_xl["인구"].values[0])
        rank_val = int(xl.sort_values("1인당", ascending=False).reset_index(drop=True).index[xl.sort_values("1인당", ascending=False).reset_index(drop=True)["구"] == gu][0]) + 1
        with kc1: st.metric("1인당 배출량", f"{v1:.2f} ㎏/일", f"전체평균 대비 {v1-avg_val:+.2f}㎏")
        with kc2: st.metric("일 총 배출량",  f"{v2:,.0f} 톤/일",  f"서울시 {rank_val}위")
        with kc3: st.metric("주민 인구",     f"{v3:,} 명")

    # 배출 시작 시각 카운트다운
    if not gu_rows.empty:
        start_str = str(gu_rows.iloc[0].get("생활쓰레기배출시작시각", "18:00"))
        end_str   = str(gu_rows.iloc[0].get("생활쓰레기배출종료시각",  "23:00"))
        now = datetime.datetime.now()
        try:
            sh, sm = map(int, start_str.replace("2400","00:00").split(":"))
            start_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            if start_dt < now:
                start_dt += datetime.timedelta(days=1)
            diff = start_dt - now
            h_left = diff.seconds // 3600
            m_left = (diff.seconds % 3600) // 60
            countdown_str = f"{h_left:02d}:{m_left:02d}"
            with kc4:
                st.markdown(f"""
                <div class="countdown-box" style="margin-top:4px">
                    <div class="countdown-label">다음 배출까지</div>
                    <div class="countdown-time">{countdown_str}</div>
                    <div class="countdown-note">{start_str} ~ {end_str}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            with kc4:
                st.markdown(f'<div class="card"><div class="card-title">배출 시간</div><div style="color:#15803D;font-size:16px;font-weight:700">{start_str} ~ {end_str}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # ── 지도 + 배출 상세
    map_col, info_col = st.columns([1.6, 1])

    with map_col:
        st.markdown('<div class="section-label">배출 위치 지도 (Google Maps)</div>', unsafe_allow_html=True)

        coord = GU_COORD.get(gu, [37.5665, 126.9780])

        # Google Maps embed (iframe)
        google_maps_url = (
            f"https://maps.google.com/maps?q={coord[0]},{coord[1]}"
            f"&z=14&output=embed&hl=ko"
        )
        st.markdown(f"""
        <div style="border-radius:14px;overflow:hidden;border:1.5px solid #E8ECF0;box-shadow:0 4px 16px rgba(0,0,0,0.08)">
            <iframe
                width="100%" height="420"
                src="{google_maps_url}"
                frameborder="0"
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
                style="display:block">
            </iframe>
        </div>
        <div style="font-size:11px;color:#8A94A6;margin-top:6px;text-align:right">
            📍 {gu} 중심 좌표 기준 · Google Maps
        </div>
        """, unsafe_allow_html=True)

    with info_col:
        st.markdown('<div class="section-label">배출 정보 상세</div>', unsafe_allow_html=True)

        if not gu_rows.empty:
            r = gu_rows.iloc[0]
            all_days = ["일","월","화","수","목","금","토"]

            # 배출 유형
            btype = r.get("배출장소유형","")
            bplace = r.get("배출장소","")
            pill_cls = "pill-green" if btype == "문전수거" else "pill-blue" if btype == "거점수거" else "pill-amber"
            st.markdown(f"""
            <div class="card">
                <div class="card-title">배출 장소</div>
                <span class="info-pill {pill_cls}">{btype}</span>
                <div style="color:#4B5563;font-size:13px;margin-top:8px;font-weight:500">{bplace}</div>
            </div>
            """, unsafe_allow_html=True)

            # 요일별 배출 현황
            st.markdown(f'<div class="card-title" style="margin-top:12px">요일별 배출 가능 품목</div>', unsafe_allow_html=True)

            cat_map = [
                ("🗑 일반쓰레기", "생활쓰레기배출요일",  "pill-amber"),
                ("♻️ 재활용",    "재활용품배출요일",    "pill-blue"),
                ("🥡 음식물",    "음식물쓰레기배출요일", "pill-green"),
            ]
            for cat_label, day_col, pcls in cat_map:
                days_str = r.get(day_col, "")
                if pd.isna(days_str): continue
                active = [d.strip() for d in str(days_str).split("+")]
                dots = "".join([
                    f'<span class="day-dot {"dot-on" if d in active else "dot-off"}">{d}</span>'
                    for d in all_days
                ])
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="font-size:12px;color:#6B7A90;margin-bottom:4px;font-weight:600">{cat_label}</div>
                    <div>{dots}</div>
                </div>
                """, unsafe_allow_html=True)

            # 배출 방법 3종
            for method_label, method_col, color in [
                ("🗑 일반쓰레기 배출방법", "생활쓰레기배출방법", "#D97706"),
                ("♻️ 재활용 배출방법",   "재활용품배출방법",   "#2563EB"),
                ("🥡 음식물 배출방법",   "음식물쓰레기배출방법","#1A7F5A"),
            ]:
                val = r.get(method_col, "")
                if pd.notna(val) and str(val).strip():
                    st.markdown(f"""
                    <div style="background:#F8FAFB;border-left:3px solid {color};
                                border-radius:0 10px 10px 0;padding:11px 14px;margin:6px 0;
                                border-top:1px solid #E8ECF0;border-right:1px solid #E8ECF0;border-bottom:1px solid #E8ECF0">
                        <div style="font-size:10px;color:#8A94A6;margin-bottom:4px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px">{method_label}</div>
                        <div style="font-size:13px;color:#1E2532;line-height:1.6;font-weight:400">{str(val).strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # 관리 부서
            dept = r.get("관리부서명","")
            tel  = r.get("관리부서전화번호","")
            if pd.notna(dept) and str(dept).strip():
                st.markdown(f"""
                <div style="background:#F0FAF5;border:1.5px solid #A8D5C2;border-radius:10px;
                            padding:12px 16px;margin-top:12px;display:flex;gap:12px;align-items:center">
                    <span style="font-size:20px">📞</span>
                    <div>
                        <div style="font-size:12px;color:#4B5563;font-weight:500">{dept}</div>
                        <div style="font-size:15px;color:#1A7F5A;font-family:'JetBrains Mono',monospace;font-weight:700;margin-top:2px">{tel}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── 구별 전체 일정표 (성북구처럼 복수 행이 있는 경우 모두 표시)
    if len(gu_rows) > 1:
        st.markdown("---")
        st.markdown(f'<div class="section-label">{gu} 구역별 배출 일정 전체 ({len(gu_rows)}개 구역)</div>', unsafe_allow_html=True)
        disp_cols = ["관리구역명","배출장소유형","배출장소",
                     "생활쓰레기배출요일","생활쓰레기배출시작시각","생활쓰레기배출종료시각",
                     "재활용품배출요일","음식물쓰레기배출요일"]
        disp_cols = [c for c in disp_cols if c in gu_rows.columns]
        st.dataframe(
            gu_rows[disp_cols].fillna("-").reset_index(drop=True),
            use_container_width=True, height=260,
        )


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 2 ─ 배출량 히트맵                               ║
# ╚══════════════════════════════════════════════════════╝
with tab2:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── 상단 KPI 전체 합계
    total_sum = float(xl["총량"].sum())
    max_row   = xl.loc[xl["1인당"].idxmax()]
    min_row   = xl.loc[xl["1인당"].idxmin()]
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("서울 일 총 배출량", f"{total_sum:,.0f} 톤/일")
    with k2: st.metric("1인당 서울 평균",  f"{xl['1인당'].mean():.2f} ㎏/일")
    with k3: st.metric("최다 배출 구",     f"{max_row['구']} {max_row['1인당']:.2f}㎏", "1위")
    with k4: st.metric("최소 배출 구",     f"{min_row['구']} {min_row['1인당']:.2f}㎏", "25위")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    left_col, right_col = st.columns([1.5, 1])

    # ── 히트맵 지도
    with left_col:
        st.markdown('<div class="section-label">자치구별 1인당 배출량 히트맵 지도</div>', unsafe_allow_html=True)

        map_mode = st.radio("표시 기준", ["1인당 배출량 (㎏/일)", "일 총 배출량 (톤/일)"],
                            horizontal=True, key="map_mode")

        m = folium.Map(
            location=[37.5665, 126.9780], zoom_start=11,
            tiles="CartoDB positron",
        )

        col_key = "1인당" if "1인당" in map_mode else "총량"
        vmin = float(xl[col_key].min())
        vmax = float(xl[col_key].max())

        for _, row in xl.iterrows():
            gname = row["구"]
            coord = GU_COORD.get(gname)
            if not coord: continue
            val   = float(row[col_key])
            ratio = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5

            # 녹색(낮음) → 황색 → 적색(높음)
            if ratio < 0.5:
                r2 = ratio * 2
                R = int(61  + (240 - 61)  * r2)
                G = int(239 + (180 - 239) * r2)
                B = int(160 + (41  - 160) * r2)
            else:
                r2 = (ratio - 0.5) * 2
                R = int(240 + (248 - 240) * r2)
                G = int(180 + (113 - 180) * r2)
                B = int(41  + (113 - 41)  * r2)
            hex_color = f"#{R:02X}{G:02X}{B:02X}"

            unit = "㎏/일" if col_key == "1인당" else "톤/일"
            rank_n = int(xl.sort_values(col_key, ascending=False).reset_index(drop=True).index[
                xl.sort_values(col_key, ascending=False).reset_index(drop=True)["구"] == gname][0]) + 1

            popup_html = f"""
            <div style="background:#FFFFFF;color:#1E293B;padding:12px;border-radius:10px;
                        border:1.5px solid #E2E8F0;font-family:sans-serif;min-width:160px;
                        box-shadow:0 4px 12px rgba(0,0,0,0.12)">
                <b style="color:#15803D;font-size:15px">{gname}</b>
                <div style="margin-top:6px;font-size:12px">
                    <span style="color:#64748B">1인당: </span>
                    <b style="color:#D97706">{row['1인당']:.2f} ㎏/일</b>
                </div>
                <div style="font-size:12px">
                    <span style="color:#64748B">총량: </span>
                    <b style="color:#2563EB">{row['총량']:,.0f} 톤/일</b>
                </div>
                <div style="font-size:12px">
                    <span style="color:#64748B">인구: </span>
                    <b style="color:#374151">{row['인구']:,.0f}명</b>
                </div>
                <div style="font-size:11px;color:#94A3B8;margin-top:4px">서울시 {rank_n}위</div>
            </div>
            """
            folium.CircleMarker(
                location=coord,
                radius=10 + ratio * 24,
                color=hex_color, fill=True, fill_color=hex_color,
                fill_opacity=0.82, weight=1.5,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"{gname}: {val:.2f} {unit}",
            ).add_to(m)

        # 범례
        legend = """
        <div style="position:fixed;bottom:24px;right:24px;z-index:9999;
                    background:#FFFFFF;border:1.5px solid #E2E8F0;border-radius:10px;
                    padding:12px 16px;font-family:sans-serif;box-shadow:0 4px 12px rgba(0,0,0,0.12)">
            <div style="color:#1E293B;font-size:11px;font-weight:700;margin-bottom:8px">배출량 수준</div>
            <div style="display:flex;align-items:center;gap:6px;font-size:10px;color:#64748B">
                <span style="color:#16A34A;font-weight:bold">●</span> 낮음
                <div style="width:80px;height:6px;background:linear-gradient(90deg,#16A34A,#F59E0B,#EF4444);border-radius:3px"></div>
                <span style="color:#EF4444;font-weight:bold">●</span> 높음
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend))
        st_folium(m, height=480, use_container_width=True)

    # ── 오른쪽: 순위 + 차트
    with right_col:
        st.markdown('<div class="section-label">1인당 배출량 순위</div>', unsafe_allow_html=True)

        sorted_xl = xl.sort_values("1인당", ascending=False).reset_index(drop=True)
        max_v = float(sorted_xl["1인당"].max())

        for i, row in sorted_xl.iterrows():
            ratio = row["1인당"] / max_v
            if ratio > 0.7:   bar_c = "#F87171"
            elif ratio > 0.4: bar_c = "#F0B429"
            else:             bar_c = "#16A34A"
            bar_w = int(ratio * 100)
            st.markdown(f"""
            <div class="rank-row">
                <span class="rank-num">{i+1:02d}</span>
                <span class="rank-gu">{row['구']}</span>
                <div class="rank-bar-wrap">
                    <div class="rank-bar" style="width:{bar_w}%;background:{bar_c}"></div>
                </div>
                <span class="rank-val">{row['1인당']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">총 배출량 상위 10구</div>', unsafe_allow_html=True)

        top10 = xl.nlargest(10, "총량").sort_values("총량")
        fig = go.Figure(go.Bar(
            x=top10["총량"], y=top10["구"], orientation="h",
            marker=dict(color=top10["총량"],
                        colorscale=[[0,"#D1FAE5"],[0.5,"#34D399"],[1,"#059669"]]),
            text=top10["총량"].apply(lambda v: f"{v:,.0f}t"),
            textposition="outside", textfont=dict(size=10, color="#374151"),
        ))
        fig.update_layout(
            height=280, showlegend=False,
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            font=dict(family="Noto Sans KR", color="#374151", size=11),
            xaxis=dict(gridcolor="#F1F5F9", showgrid=True, title="톤/일",
                       title_font=dict(color="#64748B")),
            yaxis=dict(gridcolor="#F1F5F9"),
            margin=dict(l=70, r=60, t=10, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── 하단: 버블 차트
    st.markdown("---")
    st.markdown('<div class="section-label">인구 vs 총 배출량 vs 1인당 배출량 (버블 크기 = 총량)</div>', unsafe_allow_html=True)

    fig2 = go.Figure(go.Scatter(
        x=xl["인구"], y=xl["총량"],
        mode="markers+text",
        marker=dict(
            size=xl["1인당"] / xl["1인당"].max() * 50 + 12,
            color=xl["1인당"],
            colorscale=[[0,"#D1FAE5"],[0.4,"#34D399"],[0.7,"#F59E0B"],[1,"#EF4444"]],
            showscale=True,
            colorbar=dict(title="1인당(㎏)", thickness=10,
                          tickfont=dict(color="#64748B", size=10),
                          title_font=dict(color="#64748B", size=10)),
            line=dict(color="#FFFFFF", width=1.5),
        ),
        text=xl["구"], textposition="top center",
        textfont=dict(size=9, color="#475569"),
        hovertemplate="<b>%{text}</b><br>인구: %{x:,}명<br>총량: %{y:,.0f}t/일<extra></extra>",
    ))
    fig2.update_layout(
        height=340,
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(family="Noto Sans KR", color="#374151", size=11),
        xaxis=dict(gridcolor="#F1F5F9", title="인구 (명)", title_font=dict(color="#64748B")),
        yaxis=dict(gridcolor="#F1F5F9", title="총 배출량 (톤/일)", title_font=dict(color="#64748B")),
        margin=dict(l=60, r=60, t=20, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 3 ─ 종량제 봉투 가격                            ║
# ╚══════════════════════════════════════════════════════╝
with tab3:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    search_col, filter_col1, filter_col2 = st.columns([2, 1, 1])
    with search_col:
        search_gu = st.selectbox("🔍 지역 선택", ALL_GU,
                                 index=ALL_GU.index("마포구") if "마포구" in ALL_GU else 0,
                                 key="price_gu")
    with filter_col1:
        usage_sel = st.selectbox("봉투 용도", ["생활쓰레기", "음식물쓰레기"], key="usage")
    with filter_col2:
        kind_sel  = st.selectbox("봉투 종류", ["규격봉투", "재사용규격봉투", "특수규격마대"], key="kind")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    top_col, chart_col = st.columns([1, 1.4])

    with top_col:
        st.markdown(f'<div class="section-label">{search_gu} · {usage_sel} · {kind_sel} 가격</div>', unsafe_allow_html=True)

        gu_price = price[
            (price["시군구명"] == search_gu) &
            (price["종량제봉투용도"] == usage_sel) &
            (price["종량제봉투종류"] == kind_sel)
        ]

        if gu_price.empty:
            st.markdown('<div class="card"><div style="color:#64748B;font-size:13px">해당 조건의 가격 데이터가 없습니다.</div></div>', unsafe_allow_html=True)
        else:
            for _, pr in gu_price.iterrows():
                target = pr.get("종량제봉투사용대상", "")
                sizes = [
                    ("1ℓ","1ℓ가격"), ("2ℓ","2ℓ가격"), ("3ℓ","3ℓ가격"),
                    ("5ℓ","5ℓ가격"), ("10ℓ","10ℓ가격"), ("20ℓ","20ℓ가격"),
                    ("30ℓ","30ℓ가격"), ("50ℓ","50ℓ가격"),
                    ("75ℓ","75ℓ가격"), ("100ℓ","100ℓ가격"),
                ]
                valid = [(s, int(pr[c])) for s, c in sizes if c in pr and pd.notna(pr[c]) and pr[c] > 0]
                if not valid: continue

                pill_cls = "pill-green" if target == "가정용" else "pill-blue" if target == "사업장용" else "pill-amber"
                cells_html = "".join([
                    f'<div class="price-cell">'
                    f'<div class="price-size">{sz}</div>'
                    f'<div class="price-val">{p:,}</div>'
                    f'<div class="price-won">원</div>'
                    f'</div>'
                    for sz, p in valid
                ])
                st.markdown(f"""
                <div class="card" style="margin-bottom:12px">
                    <span class="info-pill {pill_cls}">{target}</span>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(68px,1fr));gap:8px;margin-top:12px">
                        {cells_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 음식물 추가 안내
        if usage_sel == "음식물쓰레기":
            st.markdown("""
            <div style="background:#EFF6FF;border:1.5px solid #93C5FD;border-radius:10px;
                        padding:12px 16px;margin-top:8px;font-size:13px;color:#1E40AF;line-height:1.6">
                💧 <b>음식물 봉투 팁</b><br>
                물기를 최대한 제거 후 배출하면 봉투 파손 방지 및
                수거 효율 향상에 도움이 됩니다.
            </div>
            """, unsafe_allow_html=True)

    with chart_col:
        # 서울 전체 구별 가격 비교 차트
        st.markdown('<div class="section-label">서울 전체 구별 가격 비교</div>', unsafe_allow_html=True)

        size_for_chart = st.selectbox("비교 용량", ["10ℓ","20ℓ","30ℓ","50ℓ"], index=1, key="chart_size")
        size_col_name  = f"{size_for_chart}가격"

        compare_df = price[
            (price["종량제봉투용도"] == usage_sel) &
            (price["종량제봉투종류"] == kind_sel) &
            (price["종량제봉투사용대상"] == "가정용")
        ][["시군구명", size_col_name]].copy()
        compare_df = compare_df[compare_df[size_col_name] > 0].drop_duplicates("시군구명")
        compare_df = compare_df.sort_values(size_col_name, ascending=True)

        if compare_df.empty:
            st.info("해당 조건의 비교 데이터가 없습니다.")
        else:
            bar_colors = ["#059669" if g == search_gu else "#A7F3D0"
                          for g in compare_df["시군구명"]]
            fig3 = go.Figure(go.Bar(
                x=compare_df[size_col_name], y=compare_df["시군구명"],
                orientation="h",
                marker_color=bar_colors,
                text=compare_df[size_col_name].apply(lambda v: f"{int(v)}원"),
                textposition="outside",
                textfont=dict(size=10, color="#374151"),
            ))
            fig3.update_layout(
                height=max(300, len(compare_df) * 26),
                showlegend=False,
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                font=dict(family="Noto Sans KR", color="#374151", size=11),
                xaxis=dict(gridcolor="#F1F5F9", title="가격 (원)",
                           title_font=dict(color="#64748B")),
                yaxis=dict(gridcolor="#F1F5F9"),
                margin=dict(l=80, r=70, t=10, b=40),
                title=dict(
                    text=f"{usage_sel} · {kind_sel} · {size_for_chart} 가격 비교",
                    font=dict(color="#374151", size=12),
                ),
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── 하단: 전체 가격표
    st.markdown("---")
    st.markdown('<div class="section-label">서울시 전체 가격표 (가정용 · 규격봉투 · 생활쓰레기)</div>', unsafe_allow_html=True)

    full_price = price[
        (price["종량제봉투용도"] == "생활쓰레기") &
        (price["종량제봉투종류"] == "규격봉투") &
        (price["종량제봉투사용대상"] == "가정용")
    ][["시군구명","10ℓ가격","20ℓ가격","30ℓ가격","50ℓ가격"]].drop_duplicates("시군구명").sort_values("시군구명")

    def fmt_price(v):
        if pd.isna(v) or v == 0: return "-"
        return f"{int(v):,}원"

    disp = full_price.copy()
    for c in ["10ℓ가격","20ℓ가격","30ℓ가격","50ℓ가격"]:
        disp[c] = disp[c].apply(fmt_price)
    disp.columns = ["자치구","10ℓ","20ℓ","30ℓ","50ℓ"]
    st.dataframe(disp.set_index("자치구"), use_container_width=True, height=380)

    st.markdown("""
    <div style="font-size:11px;color:#94A3B8;margin-top:8px">
        ※ 가정용 규격봉투 기준 / 0원 또는 미표기는 해당 규격 미운영 / 출처: 공공데이터포털
    </div>
    """, unsafe_allow_html=True)
