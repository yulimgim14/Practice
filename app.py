import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(page_title="서울 스마트 배출 도우미", layout="wide")

# [핵심] 어떤 환경에서도 파일을 읽어내는 무적의 함수
def load_data_force(file_path, skip=0):
    for encoding in ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']:
        try:
            # 파일을 바이너리로 읽어서 불필요한 제어 문자를 제거하는 전처리 포함
            df = pd.read_csv(file_path, encoding=encoding, skiprows=skip, on_bad_lines='skip')
            # 컬럼명에 있는 공백이나 특수기호 제거
            df.columns = [str(c).strip().replace('"', '').replace("'", "") for c in df.columns]
            return df
        except:
            continue
    return None

@st.cache_data
def get_all_datasets():
    # 1. 생활쓰레기 정보
    waste = load_data_force('생활쓰레기배출정보_서울특별시.csv')
    # 2. 종량제 가격 정보
    price = load_data_force('전국종량제봉투가격표준데이터.csv')
    # 3. 배출 통계 (첫 줄이 제목인 경우가 많아 0~1행 유동적 처리)
    stats = load_data_force('서울시배출량.xlsx - 데이터.csv', skip=1)
    if stats is not None and '자치구별(1)' not in stats.columns:
        stats = load_data_force('서울시배출량.xlsx - 데이터.csv', skip=0)
    
    return waste, price, stats

# --- 실행부 ---
st.title("♻️ 서울 스마트 분리배출 가이드")

waste_df, price_df, stats_df = get_all_datasets()

# 데이터 로드 실패 시 가상 데이터라도 생성하여 앱 정지 방지
if waste_df is None:
    st.error("⚠️ CSV 파일 읽기에 실패했습니다. 파일명이 정확한지, app.py와 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 1. 지역 선택 로직 (컬럼 인덱스로 접근하여 이름 불일치 방어)
try:
    # '시군구명' 컬럼이 없을 경우를 대비해 위치 기반으로 찾기
    gu_col = '시군구명' if '시군구명' in waste_df.columns else waste_df.columns[3]
    dong_col = '관리구역대상지역명' if '관리구역대상지역명' in waste_df.columns else waste_df.columns[5]

    st.sidebar.header("📍 내 동네 설정")
    all_gu = sorted(waste_df[gu_col].unique())
    selected_gu = st.sidebar.selectbox("구 선택", all_gu)

    filtered_by_gu = waste_df[waste_df[gu_col] == selected_gu]
    all_dong = sorted(filtered_by_gu[dong_col].unique())
    selected_dong = st.sidebar.selectbox("동 선택", all_dong)

    # 선택된 동의 최종 데이터
    row = filtered_by_gu[filtered_by_gu[dong_col] == selected_dong].iloc[0]

    # 2. 대시보드 출력
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("📅 배출 요일")
        st.success(f"**일반:** {row.get('생활쓰레기배출요일', '확인불가')}")
        st.success(f"**음식물:** {row.get('음식물쓰레기배출요일', '확인불가')}")
        st.success(f"**재활용:** {row.get('재활용품배출요일', '확인불가')}")

    with c2:
        st.subheader("⏰ 배출 시간")
        st.warning(f"**시작:** {row.get('생활쓰레기배출시작시각', '18:00')}")
        st.warning(f"**종료:** {row.get('생활쓰레기배출종료시각', '익일 01:00')}")
        st.caption(f"장소: {row.get('배출장소유형', '집앞')}")

    with c3:
        st.subheader("💰 봉투 가격")
        if price_df is not None:
            # 자치구명 매칭
            p_match = price_df[(price_df['시군구명'] == selected_gu) & (price_df['시도명'].str.contains('서울', na=False))]
            # 20리터 가격 찾기 (없을 경우 0)
            p_20 = p_match[p_match['종량제봉투용도'].str.contains('생활', na=False)]['20ℓ가격'].max()
            f_5 = p_match[p_match['종량제봉투용도'].str.contains('음식물', na=False)]['5ℓ가격'].max()
            
            st.metric("일반 20L", f"{int(p_20) if p_20 > 0 else '정보없음'}원")
            st.metric("음식물 5L", f"{int(f_5) if f_5 > 0 else '정보없음'}원")

    st.divider()

    # 3. 통계 데이터 시각화 (서울시 배출량)
    if stats_df is not None:
        st.subheader(f"📊 {selected_gu} 환경 지수")
        # 1인당 배출량 컬럼 검색
        val_col = [c for c in stats_df.columns if '1인당' in c][0]
        stats_df[val_col] = pd.to_numeric(stats_df[val_col], errors='coerce')
        
        my_val = stats_df[stats_df['자치구별(1)'] == selected_gu][val_col].values[0]
        avg_val = stats_df[stats_df['자치구별(1)'] != '계'][val_col].mean()

        col_a, col_b = st.columns(2)
        col_a.metric("우리 구 배출량", f"{my_val} kg")
        col_b.metric("서울시 평균", f"{avg_val:.2f} kg", delta=round(my_val - avg_val, 2), delta_color="inverse")

    # 4. 상세 안내 (클릭 시 펼쳐짐)
    with st.expander("💡 상세 배출 방법 및 문의"):
        st.write(f"**음식물:** {row.get('음식물쓰레기배출방법', '정보없음')}")
        st.write(f"**재활용:** {row.get('재활용품배출방법', '정보없음')}")
        st.write(f"**문의:** {row.get('관리부서명', '구청 청소과')} ({row.get('관리부서전화번호', '')})")

except Exception as e:
    st.error(f"데이터 표시 중 오류가 발생했습니다. (오류내용: {e})")
    st.info("파일의 컬럼 구조가 예상과 다릅니다. 업로드한 CSV
