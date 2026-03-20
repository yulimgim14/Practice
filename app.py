import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(page_title="서울 스마트 배출 도우미", layout="wide", page_icon="📍")

# 2. 데이터 로드 (인코딩 방어막)
@st.cache_data
def load_all_data():
    def read_df(name, skip=0):
        for enc in ['utf-8-sig', 'cp949', 'utf-8']:
            try:
                return pd.read_csv(name, encoding=enc, skiprows=skip)
            except: continue
        return None

    waste = read_df('생활쓰레기배출정보_서울특별시.csv')
    price = read_df('전국종량제봉투가격표준데이터.csv')
    stats = read_df('서울시배출량.xlsx - 데이터.csv', skip=1)
    return waste, price, stats

waste_df, price_df, stats_df = load_all_data()

# 3. 데이터 로드 실패 시 강제 종료 방지
if waste_df is None:
    st.error("CSV 파일을 읽을 수 없습니다. 파일명을 확인해주세요.")
    st.stop()

# 4. 사이드바 지역 선택
st.sidebar.header("🗺️ 내 지역 설정")
gu_list = sorted(waste_df['시군구명'].dropna().unique())
target_gu = st.sidebar.selectbox("자치구", gu_list)

dong_list = sorted(waste_df[waste_df['시군구명'] == target_gu]['관리구역대상지역명'].dropna().unique())
target_dong = st.sidebar.selectbox("행정동", dong_list)

# 5. 메인 대시보드
st.title(f"♻️ {target_gu} {target_dong} 배출 가이드")

# 데이터 필터링 (오류 방지용)
try:
    info = waste_df[(waste_df['시군구명'] == target_gu) & (waste_df['관리구역대상지역명'] == target_dong)].iloc[0]
except:
    st.warning("해당 지역의 상세 정보를 찾을 수 없어 기본 정보를 표시합니다.")
    info = waste_df.iloc[0]

# 상단 3개 지표
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📦 일반 배출", info.get('생활쓰레기배출요일', '월수금'))
with c2:
    st.metric("🍎 음식물 배출", info.get('음식물쓰레기배출요일', '매일'))
with c3:
    st.metric("🕒 배출 시간", f"{info.get('생활쓰레기배출시작시각', '18:00')}부터")

st.divider()

# 6. 지도 구현 (네이버/구글 스타일의 Folium 지도)
st.subheader("📍 우리 동네 배출 위치 확인")

# 자치구별 위경도 좌표 (샘플 - 실제 서비스 시 자치구별 좌표 매핑 테이블 필요)
# 여기서는 예시로 서울 중심부 좌표를 사용합니다.
location_map = {
    "종로구": [37.573, 126.979], "중구": [37.564, 126.997], "용산구": [37.532, 126.990],
    "서초구": [37.483, 127.032], "강남구": [37.517, 127.047], "송파구": [37.514, 127.106]
}
center = location_map.get(target_gu, [37.5665, 126.9780]) # 못찾으면 서울시청

# 지도 생성
m = folium.Map(location=center, zoom_start=15, tiles="OpenStreetMap") # 혹은 Google Maps 스타일 설정 가능

# 배출 방식에 따른 마커 표시
display_text = f"{target_gu} {target_dong}: {info.get('배출장소유형', '문전수거')}"
folium.Marker(
    location=center,
    popup=display_text,
    tooltip="여기에 배출하세요!",
    icon=folium.Icon(color="green", icon="trash")
).add_to(m)

# 지도 앱에 표시
st_folium(m, width=1200, height=400)

st.divider()

# 7. 가격 및 상세 안내
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("💰 종량제 가격")
    if price_df is not None:
        p_gu = price_df[(price_df['시군구명'] == target_gu) & (price_df['시도명'].str.contains('서울', na=False))]
        p_20 = p_gu[p_gu['종량제봉투용도'].str.contains('생활', na=False)]['20ℓ가격'].max()
        st.write(f"일반 20L 가격: **{int(p_20) if p_20 > 0 else '490'}원**")
        st.caption("※ 가격은 조례에 따라 변동될 수 있습니다.")

with col_b:
    st.subheader("📞 도움말 및 문의")
    st.write(f"담당부서: {info.get('관리부서명', '청소행정과')}")
    st.write(f"전화번호: {info.get('관리부서전화번호', '02-120')}")

with st.expander("📝 올바른 분리배출 방법 보기"):
    st.write(f"**음식물:** {info.get('음식물쓰레기배출방법', '전용 봉투 사용')}")
    st.write(f"**재활용:** {info.get('재활용품배출방법', '투명 비닐 배출')}")
