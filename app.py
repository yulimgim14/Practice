import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="스마트 분리배출 도우미", layout="wide")

st.title("♻️ 스마트 분리배출 도우미 (Smart Waste Helper)")
st.markdown("---")

# 데이터 로드 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    # 배출 통계 데이터
    stats_df = pd.read_csv('서울시배출량.xlsx - 데이터.csv', skiprows=1)
    # 배출 지침 데이터
    info_df = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    return stats_df, info_df

stats_df, info_df = load_data()

# 사이드바: 자치구 선택
st.sidebar.header("📍 우리 동네 설정")
target_gu = st.sidebar.selectbox("자치구를 선택하세요", info_df['시군구명'].unique())

# --- 기능 1: 지역별 맞춤 배출 가이드 ---
st.subheader(f"✅ {target_gu} 오늘의 배출 가이드")

col1, col2 = st.columns(2)

with col1:
    # 선택된 구의 배출 정보 추출
    gu_info = info_df[info_df['시군구명'] == target_gu].iloc[0]
    
    st.info(f"**🏠 배출 방식**: {gu_info['배출장소유형']} ({gu_info['배출장소']})")
    st.warning(f"**📅 배출 요일**: {gu_info['생활쓰레기배출요일']}")
    st.error(f"**⏰ 배출 시간**: {gu_info['생활쓰레기배출시작시각']} ~ {gu_info['생활쓰레기배출종료시각']}")

with col2:
    # 현재 시간 기준 배출 가능 여부 로직 (간단 구현)
    now = datetime.now().time()
    start_time = datetime.strptime(gu_info['생활쓰레기배출시작시각'], "%H:%M").time()
    
    if now >= start_time:
        st.success("🟢 지금은 배출 가능한 시간입니다!")
    else:
        st.error("🔴 지금은 배출 시간이 아닙니다. 밤까지 기다려주세요.")

# --- 기능 2: 배출량 히트맵 및 위치 지도 ---
st.subheader("🗺️ 쓰레기 지도 & 자치구 배출 현황")

# 지도 생성 (서울 중심점)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="cartodbpositron")

# 기획안의 히트맵 데이터 적용 (예시 좌표 기반 마커 및 레이어)
# 실제 서비스 시에는 자치구별 폴리곤(GeoJSON) 데이터를 활용하여 색상을 입힐 수 있습니다.
for index, row in stats_df.iterrows():
    if row['자치구별(1)'] == '계': continue
    
    gu_name = row['자치구별(1)']
    waste_val = float(row['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'])
    
    # 배출량에 따른 마커 색상 변경 (Dark Color: 고배출 / Light Color: 저배출)
    color = 'red' if waste_val > 1.5 else 'orange' if waste_val > 0.8 else 'green'
    
    # 임의의 자치구 위치 마킹 (실제 서비스 시 구청 좌표 등 사용)
    folium.CircleMarker(
        location=[37.56 + (index*0.005), 126.97 + (index*0.005)], # 예시 좌표
        radius=waste_val * 10,
        popup=f"{gu_name}: {waste_val}kg",
        color=color,
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

folium_static(m)

# --- 기능 3: 종량제 봉투 가격 안내 ---
st.markdown("---")
st.subheader("💰 우리 동네 종량제 봉투 가격 (20리터 기준)")
st.write("서울시 평균 가격: **490원** (각 구별 상세 가격은 지역 내 판매소를 확인하세요.)")
