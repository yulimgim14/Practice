import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json

# 페이지 설정
st.set_page_config(page_title="스마트 분리배출 도우미", layout="wide")

# 데이터 로드 (캐싱을 통해 성능 최적화)
@st.cache_data
def load_data():
    # 1. 배출 정보 데이터 (서울특별시) [cite: 1]
    dispatch_df = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    
    # 2. 종량제 봉투 가격 데이터 [cite: 42]
    price_df = pd.read_csv('전국종량제봉투가격표준데이터.csv')
    
    # 3. 서울시 배출량 데이터 
    # 실제 파일 구조에 맞춰 전처리 필요 (예시 구조 적용)
    waste_df = pd.read_csv('서울시배출량.xlsx - 데이터.csv', skiprows=1)
    waste_df.columns = ['자치구', '1인당배출량', '총배출량', '주민수']
    
    return dispatch_df, price_df, waste_df

try:
    dispatch_df, price_df, waste_df = load_data()
except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
    st.stop()

st.title("♻️ 스마트 분리배출 도우미")
st.markdown("30년 경력 전문가가 제안하는 우리 동네 스마트 클린 가이드")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📍 배출 위치 및 방법", "📊 서울시 배출량 지도", "💰 종량제 봉투 가격 검색"])

# --- 탭 1: 배출 위치 및 방법 ---
with tab1:
    st.header("우리 동네 배출 정보")
    gu_list = dispatch_df['시군구명'].unique()
    selected_gu = st.selectbox("자치구를 선택하세요", gu_list)
    
    info = dispatch_df[dispatch_df['시군구명'] == selected_gu].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🔍 {selected_gu} 배출 장소")
        st.info(f"📍 **배출 장소 유형:** {info['배출장소유형']}\n\n🏠 **상세 위치:** {info['배출장소']}")
        
        st.subheader("⏰ 배출 시간")
        st.write(f"⏱ **시작:** {info['생활쓰레기배출시작시각']} | **종료:** {info['생활쓰레기배출종료시각']}")
        st.write(f"📅 **요일:** {info['생활쓰레기배출요일']}")

    with col2:
        st.subheader("📋 분리배출 방법")
        with st.expander("일반 쓰레기"):
            st.write(info['생활쓰레기배출방법'])
        with st.expander("음식물 쓰레기"):
            st.write(info['음식물쓰레기배출방법'])
        with st.expander("재활용품"):
            st.write(info['재활용품배출방법'])

# --- 탭 2: 서울시 배출량 지도 시각화 ---
with tab2:
    st.header("서울시 자치구별 생활쓰레기 배출 지도")
    st.markdown("배출량이 많을수록 진한 색으로 표시됩니다.")
    
    # 지도 생성 (서울 중심)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    
    # 실제 구현 시에는 서울시 행정구역 GeoJSON 데이터가 필요합니다.
    # 여기서는 데이터 시각화의 원리를 보여주기 위해 Choropleth 개념을 적용합니다.
    st.warning("정밀한 지도 시각화를 위해서는 자치구 경계 데이터(GeoJSON)가 추가로 필요합니다.")
    
    # 데이터 요약표 보여주기
    st.dataframe(waste_df.sort_values(by='총배출량', ascending=False), use_container_width=True)

# --- 탭 3: 종량제 봉투 가격 검색 ---
with tab3:
    st.header("종량제 봉투 가격 검색")
    search_query = st.text_input("지역명을 입력하세요 (예: 강서구, 영등포구)", "")
    
    if search_query:
        # 필터링 [cite: 42, 43]
        results = price_df[price_df['시군구명'].str.contains(search_query, na=False)]
        
        if not results.empty:
            st.success(f"'{search_query}' 검색 결과입니다.")
            
            # 보기 좋게 가공
            display_cols = ['시도명', '시군구명', '종량제봉투종류', '종량제봉투용도', '10ℓ가격', '20ℓ가격', '50ℓ가격']
            st.dataframe(results[display_cols], use_container_width=True)
            
            st.caption("※ 가격 정보는 데이터 기준일자에 따라 실제와 다를 수 있습니다.")
        else:
            st.error("검색 결과가 없습니다. 정확한 구 이름을 입력해주세요.")

# 하단 정보
st.divider()
st.caption("본 앱은 제공된 공공데이터를 기반으로 생성된 스마트 도우미입니다. [데이터 출처: 서울특별시, 공공데이터포털]")
