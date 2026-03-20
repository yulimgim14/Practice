import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="에코-서울: 스마트 분리배출 도우미", layout="wide")

@st.cache_data
def load_data_auto():
    # 현재 폴더의 모든 파일 목록 가져오기
    files = os.listdir('.')
    
    guide, amount, price = None, None, None
    
    for f in files:
        if not f.endswith('.csv'): continue
        
        # 파일 내용에 따른 자동 매칭 로직
        try:
            temp_df = pd.read_csv(f, nrows=5) # 샘플만 읽기
            cols = "".join(temp_df.columns)
            
            # 1. 배출정보 가이드 파일 찾기
            if '생활쓰레기배출요일' in cols:
                guide = pd.read_csv(f)
            # 2. 서울시 배출량 데이터 찾기
            elif '자치구별' in cols:
                # 헤더가 2줄인 특성 반영
                amount = pd.read_csv(f, header=1)
            # 3. 종량제 봉투 가격 데이터 찾기
            elif '종량제봉투종류' in cols:
                price = pd.read_csv(f)
        except:
            continue
            
    return guide, amount, price

# 데이터 로드
guide_df, amount_df, price_df = load_data_auto()

# 데이터 로드 실패 시 안내
if guide_df is None or amount_df is None or price_df is None:
    st.error("⚠️ 필요한 데이터 파일을 찾을 수 없습니다. 파일이 모두 업로드 되었는지 확인해주세요.")
    st.info("대상 파일: 서울특별시 배출정보, 서울시 배출량(데이터), 전국 종량제 가격표")
else:
    # --- UI 구성 ---
    st.sidebar.header("📍 내 동네 설정")
    districts = sorted(guide_df['시군구명'].unique())
    selected_gu = st.sidebar.selectbox("거주하시는 '구'를 선택하세요", districts)

    st.title(f"♻️ 에코-서울: {selected_gu} 가이드")
    
    tab1, tab2, tab3 = st.tabs(["📋 배출 가이드", "📊 우리동네 성적표", "💰 봉투 가격"])

    # --- TAB 1: 배출 가이드 ---
    with tab1:
        st.subheader(f"🔍 {selected_gu} 배출 규칙")
        info = guide_df[guide_df['시군구명'] == selected_gu].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("생활쓰레기 배출일", info['생활쓰레기배출요일'])
            st.info(f"⏰ 시간: {info['생활쓰레기배출시작시각']} ~ {info['생활쓰레기배출종료시각']}")
        with c2:
            st.metric("음식물 배출일", info['음식물쓰레기배출요일'])
            st.success(f"📍 장소: {info['배출장소']} ({info['배출장소유형']})")
        
        st.divider()
        st.write("**📝 상세 분리배출 방법**")
        st.caption(info['재활용품배출방법'])

    # --- TAB 2: 배출량 시각화 ---
    with tab2:
        st.subheader("📉 서울시 자치구별 1인당 배출량 비교")
        # 데이터 정제 (수치형 변환 및 '계' 제외)
        plot_df = amount_df[amount_df['자치구별(1)'] != '계'].copy()
        # 컬럼명에 줄바꿈이나 공백이 있을 수 있어 포함 여부로 확인
        target_col = [c for c in plot_df.columns if '주민 1인당' in c][0]
        plot_df[target_col] = pd.to_numeric(plot_df[target_col], errors='coerce')
        
        fig = px.bar(plot_df.sort_values(target_col), 
                     x='자치구별(1)', y=target_col,
                     color=target_col, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
        
        my_val = plot_df[plot_df['자치구별(1)'] == selected_gu][target_col].values[0]
        st.warning(f"📢 {selected_gu}의 1인당 하루 배출량은 {my_val}kg입니다. 서울시 평균을 확인해보세요!")

    # --- TAB 3: 봉투 가격 ---
    with tab3:
        st.subheader("💵 현재 판매 가격")
        # 가격 데이터 필터링
        seoul_price = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == selected_gu)]
        
        show_cols = ['종량제봉투종류', '종량제봉투용도', '10ℓ가격', '20ℓ가격', '50ℓ가격']
        # 실제 데이터에 있는 컬럼만 필터링
        available_cols = [c for c in show_cols if c in seoul_price.columns]
        st.dataframe(seoul_price[available_cols].reset_index(drop=True), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("30년 경력 쓰레기 전문가 시스템 v1.2")
