from flask import Flask, request, jsonify
import pandas as pd
import datetime

app = Flask(__name__)

# 1. 데이터 로드 (서버 시작 시 메모리에 로드하여 속도 최적화)
try:
    waste_info = pd.read_csv('생활쓰레기배출정보_서울특별시.csv')
    price_info = pd.read_csv('전국종량제봉투가격표준데이터.csv')
    stats_info = pd.read_csv('서울시배출량.xlsx - 데이터.csv')
except Exception as e:
    print(f"데이터 로드 오류: {e}")

@app.route('/api/my-region-info', methods=['GET'])
def get_region_info():
    """
    사용자가 선택한 구/동을 바탕으로 모든 CSV 데이터를 결합하여 응답
    """
    gu = request.args.get('gu')  # 예: 종로구
    dong = request.args.get('dong')  # 예: 무악동

    # --- A. 배출 요일 및 시간 (생활쓰레기배출정보) ---
    # 동 정보가 없으면 해당 구의 공통 정보를 가져옴
    region_data = waste_info[(waste_info['시군구명'] == gu) & (waste_info['관리구역대상지역명'].str.contains(dong, na=False))]
    if region_data.empty:
        region_data = waste_info[waste_info['시군구명'] == gu].head(1)

    schedule = {
        "day_normal": region_data['생활쓰레기배출요일'].values[0],
        "day_food": region_data['음식물쓰레기배출요일'].values[0],
        "day_recycle": region_data['재활용품배출요일'].values[0],
        "start_time": region_data['생활쓰레기배출시작시각'].values[0],
        "end_time": region_data['생활쓰레기배출종료시각'].values[0],
        "method": region_data['배출장소유형'].values[0],  # 문전수거 등
        "contact": region_data['관리부서전화번호'].values[0]
    }

    # --- B. 종량제 봉투 가격 (전국종량제봉투가격표준데이터) ---
    # 서울특별시 + 해당 구 필터링
    prices = price_info[(price_info['시도명'] == '서울특별시') & (price_info['시군구명'] == gu)]
    
    # 일반 쓰레기 10L, 20L 가격 추출
    normal_20l = prices[(prices['종량제봉투용도'] == '생활쓰레기') & (prices['종량제봉투사용대상'] == '가정용')]['20ℓ가격'].max()
    food_5l = prices[(prices['종량제봉투용도'] == '음식물쓰레기')]['5ℓ가격'].max()

    price_summary = {
        "normal_20l": int(normal_20l) if not pd.isna(normal_20l) else "정보없음",
        "food_5l": int(food_5l) if not pd.isna(food_5l) else "정보없음"
    }

    # --- C. 우리 동네 배출 순위 (서울시배출량 데이터) ---
    # 1인당 배출량 기준으로 정렬하여 순위 계산
    stats_info['rank'] = stats_info['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'].rank(ascending=False)
    my_gu_stats = stats_info[stats_info['자치구별(1)'] == gu]
    
    rank_info = {
        "per_person": my_gu_stats['주민 1인당 생활폐기물(쓰레기) 배출량 (㎏/인, 일)'].values[0],
        "rank": int(my_gu_stats['rank'].values[0]),
        "total_gu_count": 25
    }

    # --- 최종 응답 데이터 구성 ---
    response = {
        "region": f"{gu} {dong}",
        "schedule": schedule,
        "prices": price_summary,
        "environment_rank": rank_info,
        "message": f"오늘 {gu}의 배출 시작 시간은 {schedule['start_time']}입니다!"
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
