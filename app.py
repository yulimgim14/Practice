import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="에코-서울: 스마트 분리배출 도우미", layout="wide")

@st.cache_data
def load_data():
    # 파일 로드 (파일명은 사용자가 제공한 이름 기준)
    guide = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    # 서울시배출량 데이터는 헤더가 2줄이므로 header=1 설정
    amount = pd.read_csv('서울시배출량.xlsx - 데이터.csv', header=1)
    price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
    return guide, amount, price

try:
    guide_df, amount_df, price_df = load_data()

    # 2. 사이드바: 지역 선택
    st.sidebar.header("📍 내 동네 설정")
    districts = sorted(guide_df['시군구명'].unique())
    selected_gu = st.sidebar.selectbox("거주하시는 '구'를 선택하세요", districts)

    st.title(f"♻️ 에코-서울: {selected_gu} 가이드")

    # 3. 메인 화면 - 3분할 구성
    tab1, tab2, tab3 = st.tabs(["📋 배출 가이드", "📊 우리동네 성적표", "💰 봉투 가격"])

    # --- TAB 1: 배출 가이드 (생활쓰레기배출정보 활용) ---
    with tab1:
        st.subheader(f"🔍 {selected_gu} 배출 규칙")
        info = guide_df[guide_df['시군구명'] == selected_gu].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("생활쓰레기 배출일", info['생활쓰레기배출요일'])
            st.info(f"⏰ 배출 시간: {info['생활쓰레기배출시작시각']} ~ {info['생활쓰레기배출종료시각']}")
        with c2:
            st.metric("음식물 배출일", info['음식물쓰레기배출요일'])
            st.success(f"📍 배출 장소: {info['배출장소']} ({info['배출장소유형']})")
        
        st.divider()
        st.write("**📝 상세 분리배출 방법**")
        st.caption(info['재활용품배출방법'])

    # --- TAB 2: 배출량 시각화 (서울시배출량 데이터 활용) ---
    with tab2:
        st.subheader("📉 자치구별 1인당 쓰레기 배출량 비교")
        # '계' 데이터 제외 및 수치 변환
        plot_df = amount_df[amount_df['자치구별(1)'] != '계'].copy()
        target_col = '주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'
        plot_df[target_col] = pd.to_numeric(plot_df[target_col], errors='coerce')
        
        # 그래프 생성
        fig = px.bar(plot_df.sort_values(target_col), 
                     x='자치구별(1)', y=target_col,
                     color=target_col, color_continuous_scale='YlOrRd')
        st.plotly_chart(fig, use_container_width=True)
        
        # 전문가 멘트
        my_val = plot_df[plot_df['자치구별(1)'] == selected_gu][target_col].values[0]
        st.warning(f"💡 {selected_gu}의 1인당 하루 배출량은 {my_val}kg입니다. 분리수거를 더 철저히 합시다!")

    # --- TAB 3: 봉투 가격 (종량제봉투가격 데이터 활용) ---
    with tab3:
        st.subheader("💵 현재 판매 가격 (서울 기준)")
        seoul_price = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == selected_gu)]
        
        # 주요 규격만 선택해서 보여주기
        cols_to_show = ['종량제봉투종류', '종량제봉투용도', '10ℓ가격', '20ℓ가격', '50ℓ가격']
        st.dataframe(seoul_price[cols_to_show].reset_index(drop=True), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
    st.info("파일명과 데이터 형식을 확인해주세요.")
