import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="에코-서울: 스마트 분리배출 도우미", layout="wide")

# 데이터 로드 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    # 1. 배출 정보 가이드
    guide_df = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    # 2. 서울시 배출량 통계
    amount_df = pd.read_csv('서울시배출량.xlsx - 데이터.csv', skiprows=1) # 헤더 처리
    # 3. 종량제 봉투 가격
    price_df = pd.read_csv('전국종량제봉투가격표준데이터.csv')
    return guide_df, amount_df, price_df

guide_df, amount_df, price_df = load_data()

# 사이드바: 지역 선택
st.sidebar.header("📍 지역 설정")
seoul_districts = sorted(guide_df['시군구명'].unique())
selected_district = st.sidebar.selectbox("거주하시는 '구'를 선택하세요", seoul_districts)

# 메인 타이틀
st.title("♻️ 에코-서울 (Eco-Seoul)")
st.markdown(f"**30년차 전문가가 알려주는 {selected_district} 맞춤형 배출 가이드**")

# --- Section 1: 실시간 배출 가이드 ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 배출 일정 & 방법")
    district_info = guide_df[guide_df['시군구명'] == selected_district].iloc[0]
    
    st.info(f"**배출 요일:** {district_info['생활쓰레기배출요일']}")
    st.warning(f"**배출 시간:** {district_info['생활쓰레기배출시작시각']} ~ {district_info['생활쓰레기배출종료시각']}")
    st.success(f"**배출 장소:** {district_info['배출장소']} ({district_info['배출장소유형']})")

with col2:
    st.subheader("💡 올바른 분리배출법")
    with st.expander("재활용품 버리는 법"):
        st.write(district_info['재활용품배출방법'])
    with st.expander("음식물 쓰레기 처리"):
        st.write(district_info['음식물쓰레기배출방법'])

# --- Section 2: 서울시 배출량 현황 시각화 ---
st.divider()
st.subheader("📊 서울시 자치구별 배출 성적표")

# 데이터 정리
amount_df = amount_df[amount_df['자치구별(1)'] != '계']
# 1인당 배출량 기준으로 정렬
amount_df = amount_df.sort_values(by='주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)', ascending=False)

fig = px.bar(amount_df, 
             x='자치구별(1)', 
             y='주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)',
             title="자치구별 1인당 일일 쓰레기 배출량 (kg)",
             color='주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)',
             color_continuous_scale='Reds')

st.plotly_chart(fig, use_container_width=True)

# 전문가 코멘트
my_district_rank = amount_df.reset_index().index[amount_df['자치구별(1)'] == selected_district].tolist()[0] + 1
st.write(f"📢 **전문가 한마디:** {selected_district}는 서울시 25개구 중 배출량 **{my_district_rank}위**입니다. 조금만 더 분리배출에 힘써주세요!")

# --- Section 3: 종량제 봉투 가격 정보 ---
st.divider()
st.subheader("💰 우리 동네 봉투 가격")

seoul_prices = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == selected_district)]
if not seoul_prices.empty:
    st.dataframe(seoul_prices[['종량제봉투종류', '종량제봉투용도', '10ℓ가격', '20ℓ가격', '50ℓ가격', '100ℓ가격']], use_container_width=True)
else:
    st.write("해당 지역의 가격 데이터를 찾을 수 없습니다.")

# 하단 푸터
st.caption("Data Source: 공공데이터포털, 서울시 열린데이터광장 | 30년차 쓰레기 전문가 자문")
