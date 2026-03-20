import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="에코-서울: 스마트 분리배출 도우미", layout="wide")

@st.cache_data
def load_data():
    try:
        # 1. 서울시 배출 가이드 (생활쓰레기배출정보_서울특별시.csv 활용)
        guide = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
        
        # 2. 서울시 배출량 통계 (헤더 처리 중요: 0행은 연도, 1행이 실제 컬럼명)
        # 파일 구조상 2번째 줄(index 1)부터 컬럼명으로 읽어옵니다.
        amount = pd.read_csv('서울시배출량.xlsx - 데이터.csv', header=1)
        
        # 3. 종량제 봉투 가격
        price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
        
        return guide, amount, price
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None, None, None

guide_df, amount_df, price_df = load_data()

if guide_df is not None:
    # 사이드바 설정
    st.sidebar.header("📍 내 동네 설정")
    # 시군구명 중복 제거 및 정렬
    districts = sorted(guide_df['시군구명'].unique())
    selected_gu = st.sidebar.selectbox("거주하시는 '구'를 선택하세요", districts)

    # 메인 섹션
    st.title("♻️ 에코-서울 (Eco-Seoul)")
    st.markdown(f"### **{selected_gu}** 맞춤형 분리배출 서비스")

    # --- Section 1: 우리 동네 배출 가이드 ---
    st.divider()
    col1, col2 = st.columns(2)
    
    # 해당 구의 첫 번째 데이터 추출
    district_data = guide_df[guide_df['시군구명'] == selected_gu].iloc[0]

    with col1:
        st.subheader("📅 배출 시간 및 장소")
        st.info(f"**생활쓰레기:** {district_data['생활쓰레기배출요일']} ({district_data['생활쓰레기배출시작시각']}~{district_data['생활쓰레기배출종료시각']})")
        st.info(f"**음식물쓰레기:** {district_data['음식물쓰레기배출요일']}")
        st.success(f"**배출 장소:** {district_data['배출장소']} ({district_data['배출장소유형']})")
        st.warning(f"**미수거일:** {district_data['미수거일']}")

    with col2:
        st.subheader("💡 분리배출 핵심 요령")
        with st.expander("✅ 재활용품 배출 방법", expanded=True):
            st.write(district_data['재활용품배출방법'])
        st.write(f"📞 **문의처:** {district_data['관리부서명']} ({district_data['관리부서전화번호']})")

    # --- Section 2: 서울시 배출량 통계 (시각화) ---
    st.divider()
    st.subheader("📊 자치구별 쓰레기 배출량 비교 (2024)")
    
    # 데이터 정제: '계' 제외 및 수치형 변환
    vis_df = amount_df[amount_df['자치구별(1)'] != '계'].copy()
    y_col = '주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'
    vis_df[y_col] = pd.to_numeric(vis_df[y_col], errors='coerce')
    vis_df = vis_df.sort_values(by=y_col, ascending=False)

    fig = px.bar(vis_df, x='자치구별(1)', y=y_col,
                 title="자치구별 1인당 일일 배출량 (kg)",
                 labels={y_col: '배출량(kg)', '자치구별(1)': '구이름'},
                 color=y_col, color_continuous_scale='Reds')
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Section 3: 종량제 봉투 가격 ---
    st.divider()
    st.subheader("💰 실시간 종량제 봉투 가격")
    
    # 서울시 + 선택한 구 필터링
    local_prices = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == selected_gu)]
    
    if not local_prices.empty:
        # 보기 편하게 주요
