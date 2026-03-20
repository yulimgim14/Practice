import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="스마트 분리배출 도우미", layout="wide")

@st.cache_data
def load_data():
    # 파일명은 업로드하신 파일명과 정확히 일치해야 합니다.
    waste = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
    stats = pd.read_csv('서울시배출량.xlsx - 데이터.csv')
    return waste, price, stats

try:
    waste_df, price_df, stats_df = load_data()

    st.title("♻️ 스마트 분리배출 도우미")
    st.markdown("### 우리 동네 쓰레기 배출 정보를 한눈에 확인하세요.")

    # 사이드바: 지역 선택
    st.sidebar.header("📍 지역 설정")
    target_gu = st.sidebar.selectbox("자치구를 선택하세요", sorted(waste_df['시군구명'].unique()))
    
    dongs = waste_df[waste_df['시군구명'] == target_gu]['관리구역대상지역명'].unique()
    target_dong = st.sidebar.selectbox("동을 선택하세요", sorted(dongs))

    # 데이터 필터링
    region_info = waste_df[(waste_df['시군구명'] == target_gu) & (waste_df['관리구역대상지역명'] == target_dong)].iloc[0]
    
    # 레이아웃 구성
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("⏰ 배출 일정")
        st.info(f"**일반쓰레기:** {region_info['생활쓰레기배출요일']}")
        st.info(f"**음식물:** {region_info['음식물쓰레기배출요일']}")
        st.info(f"**재활용품:** {region_info['재활용품배출요일']}")
        st.warning(f"🕒 시간: {region_info['생활쓰레기배출시작시각']} ~ {region_info['생활쓰레기배출종료시각']}")

    with col2:
        st.subheader("💰 봉투 가격 (가정용)")
        # 서울시 + 해당 구 필터링
        gu_price = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == target_gu)]
        
        n_20 = gu_price[gu_price['종량제봉투용도'] == '생활쓰레기']['20ℓ가격'].max()
        f_5 = gu_price[gu_price['종량제봉투용도'] == '음식물쓰레기']['5ℓ가격'].max()
        
        st.metric("일반 20L", f"{int(n_20) if not pd.isna(n_20) else '확인불가'}원")
        st.metric("음식물 5L", f"{int(f_5) if not pd.isna(f_5) else '확인불가'}원")
        st.caption(f"📍 배출장소: {region_info['배출장소유형']}")

    with col3:
        st.subheader("📊 우리 동네 배출 현황")
        # 배출량 통계 가공
        stats_clean = stats_df.copy()
        # '계' 행 제외 및 수치형 변환
        stats_clean = stats_clean[stats_clean['자치구별(1)'] != '계']
        stats_clean['배출량'] = pd.to_numeric(stats_clean['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'])
        stats_clean['순위'] = stats_clean['배출량'].rank(ascending=False)
        
        my_stat = stats_clean[stats_clean['자치구별(1)'] == target_gu].iloc[0]
        
        st.write(f"**{target_gu}**의 1인당 배출량")
        st.title(f"{my_stat['배출량']}kg")
        st.write(f"서울시 25개 구 중 **{int(my_stat['순위'])}위**")

    st.divider()
    
    # 배출 방법 안내
    with st.expander("💡 올바른 배출 방법 자세히 보기"):
        st.write(f"**음식물:** {region_info['음식물쓰레기배출방법']}")
        st.write(f"**재활용:** {region_info['재활용품배출방법']}")
        st.write(f"**대형폐기물:** {region_info['일시적다량폐기물배출방법']}")
        st.write(f"📞 **문의처:** {region_info['관리부서명']} ({region_info['관리부서전화번호']})")

except Exception as e:
    st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
    st.write("CSV 파일명들이 코드와 일치하는지 확인해주세요.")
