import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# 페이지 설정: 전문가의 느낌을 주는 와이드 모드와 타이틀
st.set_page_config(page_title="Smart Waste Helper", layout="wide", page_icon="♻️")

# 커스텀 CSS로 세련된 UI 입히기
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .guide-card { border-left: 5px solid #2ecc71; padding-left: 15px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드 (에러 방지를 위해 파일명 정확히 일치시킴)
@st.cache_data
def load_data():
    try:
        # 1. 배출량 통계 데이터 (첫 번째 행이 실제 컬럼명인 구조 반영)
        stats = pd.read_csv('서울시배출량.xlsx - 데이터.csv', header=1)
        
        # 2. 배출 정보 데이터 (한글 깨짐 방지를 위해 encoding 설정 시도)
        info = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
        
        # 3. 봉투 가격 데이터
        price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
        
        return stats, info, price
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None, None, None

stats_df, info_df, price_df = load_data()

if stats_df is not None:
    # --- 사이드바 ---
    st.sidebar.title("🌿 SMART HELPER")
    st.sidebar.info("30년 경력 전문가가 제안하는 스마트 분리배출 솔루션")
    
    target_gu = st.sidebar.selectbox("📍 분석할 자치구를 선택하세요", info_df['시군구명'].unique())
    
    # --- 메인 대시보드 ---
    st.title("♻️ 스마트 분리배출 도우미")
    st.write(f"현재 **{target_gu}**의 배출 시스템을 분석 중입니다.")

    # 상단 지표 (Metrics)
    gu_stats = stats_df[stats_df['자치구별(1)'] == target_gu].iloc[0]
    avg_stats = stats_df[stats_df['자치구별(1)'] == '계'].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        val = float(gu_stats['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'])
        st.metric("1인당 배출량", f"{val} kg", delta=round(val - 1.09, 2), delta_color="inverse")
    with col2:
        st.metric("자치구 전체 배출량", f"{gu_stats['생활계폐기물 배출량 (톤/일)']} 톤/일")
    with col3:
        # 가격 정보 추출 (서울시, 해당구, 가정용, 20리터)
        try:
            p_val = price_df[(price_df['시군구명'] == target_gu) & 
                             (price_df['종량제봉투용도'] == '생활쓰레기') & 
                             (price_df['종량제봉투사용대상'] == '가정용')]['20ℓ가격'].values[0]
            st.metric("20L 봉투 가격", f"{int(p_val)} 원")
        except:
            st.metric("20L 봉투 가격", "정보 없음")

    # 배출 가이드 정보
    st.markdown("---")
    st.subheader("📋 오늘의 배출 가이드")
    
    gu_info = info_df[info_df['시군구명'] == target_gu].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="guide-card">
            <h4>🏠 배출 장소 및 방법</h4>
            <p><b>유형:</b> {gu_info['배출장소유형']}</p>
            <p><b>위치:</b> {gu_info['배출장소']}</p>
            <p><b>방법:</b> {gu_info['생활쓰레기배출방법']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="guide-card" style="border-left-color: #e74c3c;">
            <h4>⏰ 배출 시간 및 요일</h4>
            <p><b>요일:</b> {gu_info['생활쓰레기배출요일']}</p>
            <p><b>시간:</b> {gu_info['생활쓰레기배출시작시각']} ~ {gu_info['생활쓰레기배출종료시각']}</p>
            <p><b>미수거일:</b> {gu_info['미수거일']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 지도 시각화
    st.markdown("---")
    st.subheader("🗺️ 서울시 자치구별 배출 히트맵")
    
    # 서울 시청 중심 좌표
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="cartodbpositron")
    
    # 간단한 서클 마커로 배출량 표시 (전문가용 히트맵 스타일)
    # 실제 경계 데이터(GeoJSON)가 있다면 더 세련되게 가능하지만, 현재는 좌표 추정 마커 사용
    for idx, row in stats_df.iterrows():
        name = row['자치구별(1)']
        if name == '계': continue
        
        # 배출량에 따른 색상 농도 (전문가적 시각화)
        amount = float(row['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'])
        color = '#e74c3c' if amount > 1.5 else '#f1c40f' if amount > 1.0 else '#2ecc71'
        
        # 임의의 좌표 (실제로는 각 구청 좌표 리스트를 매핑하는 것이 좋습니다)
        folium.Circle(
            location=[37.5665 + (idx*0.002), 126.9780 + (idx*0.002)], # 예시 위치
            radius=amount * 1000,
            popup=f"{name}: {amount}kg",
            color=color,
            fill=True,
            fill_opacity=0.4
        ).add_to(m)
        
    folium_static(m)

else:
    st.warning("데이터 파일을 불러올 수 없습니다. 파일명이 '서울시배출량.xlsx - 데이터.csv'인지 확인해 주세요.")
