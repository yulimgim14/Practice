import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울 쓰레기 배출 도우미", layout="wide")

# 2. 데이터 로드 함수 (에러 방지를 위해 하나씩 로드)
@st.cache_data
def load_all_data():
    try:
        # 파일명을 정확히 매칭 (사용자가 업로드한 파일명 기준)
        waste = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
        price = pd.read_csv('전국종량제봉투가격표준데이터.csv')
        stats = pd.read_csv('서울시배출량.xlsx - 데이터.csv')
        return waste, price, stats
    except Exception as e:
        st.error(f"파일을 찾을 수 없거나 읽는 중 오류가 발생했습니다: {e}")
        return None, None, None

waste_df, price_df, stats_df = load_all_data()

if waste_df is not None:
    st.title("♻️ 스마트 분리배출 도우미")

    # 3. 데이터 정제 (비어있는 값 처리)
    waste_df['관리구역대상지역명'] = waste_df['관리구역대상지역명'].fillna("전체")
    
    # 4. 사이드바 지역 선택
    st.sidebar.header("📍 지역 선택")
    gu_list = sorted(waste_df['시군구명'].unique())
    target_gu = st.sidebar.selectbox("자치구", gu_list)
    
    dong_list = sorted(waste_df[waste_df['시군구명'] == target_gu]['관리구역대상지역명'].unique())
    target_dong = st.sidebar.selectbox("행정동", dong_list)

    # 5. 메인 화면 레이아웃
    try:
        # 해당 동 데이터 추출
        filtered_waste = waste_df[(waste_df['시군구명'] == target_gu) & 
                                  (waste_df['관리구역대상지역명'] == target_dong)]
        
        if not filtered_waste.empty:
            info = filtered_waste.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 배출 스케줄")
                st.success(f"**일반쓰레기:** {info['생활쓰레기배출요일']}")
                st.success(f"**음식물:** {info['음식물쓰레기배출요일']}")
                st.success(f"**재활용품:** {info['재활용품배출요일']}")
                st.info(f"⏰ **시간:** {info['생활쓰레기배출시작시각']} ~ {info['생활쓰레기배출종료시각']}")
                st.caption(f"📍 배출장소: {info['배출장소유형']} ({info.get('배출장소', '집앞')})")

            with col2:
                st.subheader("💰 봉투 가격 정보")
                # 서울시 + 선택한 구 가격 필터링
                gu_price = price_df[(price_df['시도명'] == '서울특별시') & (price_df['시군구명'] == target_gu)]
                
                # 가격 데이터가 있을 경우 가장 보편적인 규격 표시
                try:
                    p_20l = gu_price[gu_price['종량제봉투용도'] == '생활쓰레기']['20ℓ가격'].values[0]
                    f_5l = gu_price[gu_price['종량제봉투용도'] == '음식물쓰레기']['5ℓ가격'].values[0]
                    
                    st.metric("일반용 20L", f"{int(p_20l)}원")
                    st.metric("음식물 5L", f"{int(f_5l)}원")
                except:
                    st.warning("이 지역의 가격 정보를 불러올 수 없습니다.")

            st.divider()

            # 6. 환경 통계 (서울시 배출량 데이터 활용)
            st.subheader("📊 우리 동네 환경 지표")
            if stats_df is not None:
                # 데이터 행 정리 (첫 두 줄이 헤더인 경우 처리)
                stats_clean = stats_df[stats_df['자치구별(1)'] != '계'].copy()
                # 수치 변환 시 에러 방지
                stats_clean['배출량'] = pd.to_numeric(stats_clean['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'], errors='coerce')
                
                gu_stat = stats_clean[stats_clean['자치구별(1)'] == target_gu]
                if not gu_stat.empty:
                    val = gu_stat['배출량'].values[0]
                    # 전체 평균 계산
                    avg_val = stats_clean['배출량'].mean()
                    
                    c1, c2 = st.columns(2)
                    c1.write(f"**{target_gu}** 1인당 하루 배출량")
                    c1.title(f"{val} kg")
                    c2.write("서울시 자치구 평균")
                    c2.title(f"{avg_val:.2f} kg")
                    
                    if val > avg_val:
                        st.error("⚠️ 우리 지역은 서울시 평균보다 배출량이 많습니다. 분리배출에 신경 써주세요!")
                    else:
                        st.balloons()
                        st.success("✅ 우리 지역은 서울시 평균보다 깨끗하게 관리되고 있습니다!")

            # 7. 상세 가이드
            with st.expander("📝 상세 배출 방법 안내"):
                st.write(f"**[음식물]** {info['음식물쓰레기배출방법']}")
                st.write(f"**[재활용]** {info['재활용품배출방법']}")
                st.write(f"**[문의처]** {info['관리부서명']}: {info['관리부서전화번호']}")

        else:
            st.warning("선택하신 지역의 세부 정보를 찾을 수 없습니다.")

    except Exception as e:
        st.error(f"데이터 표시 중 오류가 발생했습니다: {e}")

else:
    st.info("데이터 파일을 업로드하거나 파일명을 확인해주세요.")
