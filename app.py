import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="서울 스마트 배출 도우미", layout="wide", page_icon="♻️")

# 2. 유연한 데이터 로드 함수 (인코딩/오류 방어)
def load_csv_safely(file_name, skip_rows=0):
    try:
        # 다양한 인코딩 시도
        for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
            try:
                df = pd.read_csv(file_name, encoding=enc, skiprows=skip_rows)
                # 컬럼명 양끝 공백 제거 및 문자열화
                df.columns = [str(c).strip() for c in df.columns]
                return df
            except:
                continue
        return None
    except:
        return None

@st.cache_data
def get_all_data():
    # 각 파일별 특성에 맞춘 로딩
    waste = load_csv_safely('생활쓰레기배출정보_서울특별시.csv')
    price = load_csv_safely('전국종량제봉투가격표준데이터.csv')
    # 배출량 데이터는 보통 첫 줄이 메타정보라 한 줄 건너뜀
    stats = load_csv_safely('서울시배출량.xlsx - 데이터.csv', skip_rows=1)
    return waste, price, stats

# 데이터 로드 실행
waste_df, price_df, stats_df = get_all_data()

# --- UI 시작 ---
st.title("♻️ 스마트 분리배출 도우미")

# 데이터가 하나라도 로드되지 않았을 때의 방어 로직
if waste_df is None:
    st.error("⚠️ CSV 파일을 찾을 수 없거나 형식이 잘못되었습니다. 파일명을 확인해주세요.")
    st.stop()

# 3. 사이드바: 지역 선택 (데이터 기반 동적 생성)
st.sidebar.header("📍 내 지역 설정")

# 자치구 선택
gu_col = '시군구명' if '시군구명' in waste_df.columns else waste_df.columns[3]
gu_list = sorted(waste_df[gu_col].unique())
selected_gu = st.sidebar.selectbox("자치구를 선택하세요", gu_list)

# 행정동 선택
dong_col = '관리구역대상지역명' if '관리구역대상지역명' in waste_df.columns else waste_df.columns[5]
dong_df = waste_df[waste_df[gu_col] == selected_gu]
dong_list = sorted(dong_df[dong_col].unique())
selected_dong = st.sidebar.selectbox("동을 선택하세요", dong_list)

# 4. 메인 정보 디스플레이
try:
    # 해당 동 데이터 1건 추출
    target_data = dong_df[dong_df[dong_col] == selected_dong].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⏰ 이번 주 배출 요일")
        # 데이터에 컬럼이 없을 경우를 대비한 .get() 활용
        st.info(f"**일반쓰레기:** {target_data.get('생활쓰레기배출요일', '확인 필요')}")
        st.info(f"**음식물쓰레기:** {target_data.get('음식물쓰레기배출요일', '확인 필요')}")
        st.info(f"**재활용품:** {target_data.get('재활용품배출요일', '확인 필요')}")
        
        st.warning(f"🕒 **시간:** {target_data.get('생활쓰레기배출시작시각', '18:00')} ~ {target_data.get('생활쓰레기배출종료시각', '01:00')}")

    with col2:
        st.subheader("💰 봉투 가격 (가정용)")
        if price_df is not None:
            # 서울 + 해당 구 필터링
            p_gu = price_df[(price_df['시도명'].str.contains('서울', na=False)) & 
                            (price_df['시군구명'] == selected_gu)]
            
            # 일반 20L 가격 (가장 큰 값을 가져옴)
            p_20 = p_gu[p_gu['종량제봉투용도'].str.contains('생활', na=False)]['20ℓ가격'].max()
            f_5 = p_gu[p_gu['종량제봉투용도'].str.contains('음식물', na=False)]['5ℓ가격'].max()

            c1, c2 = st.columns(2)
            c1.metric("일반 20L", f"{int(p_20) if p_20 > 0 else '정보없음'}원")
            c2.metric("음식물 5L", f"{int(f_5) if f_5 > 0 else '정보없음'}원")
        
        st.write(f"🏠 **배출 장소:** {target_data.get('배출장소유형', '집앞 배출')}")

    st.divider()

    # 5. 환경 리포트 (통계 데이터 시각화)
    if stats_df is not None:
        st.subheader(f"📊 {selected_gu} 배출 통계")
        # '주민 1인당'이 포함된 컬럼 찾기
        stat_col = [c for c in stats_df.columns if '1인당' in c]
        if stat_col:
            # 수치 데이터로 강제 변환
            stats_df[stat_col[0]] = pd.to_numeric(stats_df[stat_col[0]], errors='coerce')
            gu_val = stats_df[stats_df['자치구별(1)'] == selected_gu][stat_col[0]].values[0]
            avg_val = stats_df[stats_df['자치구별(1)'] != '계'][stat_col[0]].mean()

            st.write(f"우리 동네 1인당 하루 쓰레기 배출량은 **{gu_val}kg** 입니다.")
            st.progress(min(float(gu_val/2), 1.0)) # 2kg를 맥스로 잡은 게이지
            
            if gu_val > avg_val:
                st.write("😔 서울시 평균보다 조금 더 배출하고 있어요.")
            else:
                st.write("✨ 서울시 평균보다 적게 배출하는 모범 지역입니다!")

    # 6. 상세 안내 (Expander)
    with st.expander("💡 상세 배출 방법 및 문의처"):
        st.write(f"**음식물:** {target_data.get('음식물쓰레기배출방법', '정보없음')}")
        st.write(f"**재활용:** {target_data.get('재활용품배출방법', '정보없음')}")
        st.write(f"📞 **문의처:** {target_data.get('관리부서명', '구청 청소과')} ({target_data.get('관리부서전화번호', '')})")

except Exception as e:
    st.error(f"데이터 매칭 중 오류가 발생했습니다. (원인: {e})")
    st.info("파일의 컬럼명이 코드와 다를 수 있습니다. CSV 파일을 확인해주세요.")
