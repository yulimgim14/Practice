import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="에코-서울: 스마트 분리배출 도우미", layout="wide")

# 데이터 로드 함수 (오류 방지를 위한 예외 처리 강화)
@st.cache_data
def load_data():
    try:
        # 1. 서울시 배출 가이드 (생활쓰레기배출정보_서울특별시.csv)
        guide = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
        
        # 2. 서울시 배출량 통계 (헤더가 두 줄일 경우를 대비해 처리)
        # 0번째 줄은 '자치구별(1), 2024, 2024...' / 1번째 줄은 실제 컬럼명
        amount = pd.read_csv('서울시배출량.xlsx - 데이터.csv', header=1)
        
        # 3. 종량제 봉투 가격
        price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
        
        return guide, amount, price
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return None, None, None

guide_df, amount_df, price_df = load_data()

if guide_df is not None:
    # 사이드바: 자치구 선택
    st.sidebar.header("📍 내 동네 설정")
    districts = sorted(guide_df['시군구명'].unique())
    selected_gu = st.sidebar.selectbox("거주하시는 '구'를 선택하세요", districts)

    # 메인 타이틀
    st.title("♻️ 에코-서울 (Eco-Seoul)")
    st.markdown(f"### **{selected_gu}** 맞춤형 분리배출 가이드")

    # --- Section 1: 우리 동네 배출 규칙 (지도 대신 상세 정보로 구현) ---
    st.divider()
    col1, col2 = st.columns(2)
    
    # 해당 구의 데이터 추출 (첫 번째 행 기준)
    district_data = guide_df[guide_df['시군구명'] == selected_gu].iloc[0]

    with col1:
        st.subheader("📅 언제 어디에 버리나요?")
        st.info(f"**생활쓰레기 요일:** {district_data['생활쓰레기배출요일']}")
        st.info(f"**음식물쓰레기 요일:** {district_data['음식물쓰레기배출요일']}")
        st.warning(f"**배출 시간:** {district_data['생활쓰레기배출시작시각']} ~ {district_data['생활쓰레기배출종료시각']}")
        st.success(f"**배출 장소:** {district_data['배출장소']} ({district_data['배출장소유형']})")

    with col2:
        st.subheader("💡 올바른 배출 방법")
        with st.expander("📝 재활용품 분리배출 상세", expanded=True):
            st.write(district_data['재활용품배출방법'])
        with st.expander("🍽️ 음식물쓰레기 배출 상세"):
            st.write(district_data['음식물쓰레기배출방법'])
        st.write(f"📞 **문의처:** {district_data['관리부서명']} ({district_data['관리부서전화번호']})")

    # --- Section 2: 배출량 시각화 (서울시배출량 데이터 활용) ---
    st.divider()
    st.subheader("📊 서울시 자치구별 쓰레기 배출 현황 (2024)")
    
    # '계' 행 제외 및 컬럼명 정제
    vis_df = amount_df[amount_df['자치구별(1)'] != '계'].copy()
    val_col = '주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'
    
    # 데이터 타입 변환 (문자열일 경우 대비)
    vis_df[val_col] = pd.to_numeric(vis_df[val_col], errors='coerce')
    vis_df = vis_df.sort_values(by=val_col, ascending=False)

    fig = px.bar(vis_df, x='자치구별(1)', y=val_col,
                 labels={val_col: '배출량(kg/일)', '자치구별(1)': '자치구'},
                 color=val_col, color_continuous_scale='OrRd')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 해당 구의 순위 계산
    rank = vis_df['자치구별(1)'].tolist().index(selected_gu) + 1
    st.markdown(f"**📢 전문가 코멘트:** {selected_gu}는 서울시에서 1인당 배출량이 **{rank}번째**로 많습니다. 분리배출에 더 신경 써주세요!")

    # --- Section 3: 종량제 봉투 가격 정보 ---
    st.divider()
    st.subheader("💰 종량제 봉투 가격 안내")
    
    # 서울시 & 해당 구 데이터 필터링
    local_price = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == selected_gu)]
    
    if not local_price.empty:
        # 주요 규격만 선별하여 표시
        display_cols = ['종량제봉투종류', '종량제봉투용도', '5ℓ가격', '10ℓ가격', '20ℓ가격', '50ℓ가격', '100ℓ가격']
        st.dataframe(local_price[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("죄송합니다. 해당 자치구의 봉투 가격 데이터를 찾을 수 없습니다.")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 에코-서울 | 30년차 배출 전문가 가이드")
