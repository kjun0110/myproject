from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import os
from typing import List, Dict, Any

app = FastAPI(
    title="Titanic Service",
    description="Titanic 데이터 분석 서비스",
    version="1.0.0",
)

# CORS는 게이트웨이에서 처리하므로 여기서는 설정하지 않음

# CSV 파일 경로
csv_path = os.path.join(os.path.dirname(__file__), 'train.csv')

def get_top_10_passengers() -> List[Dict[str, Any]]:
    """요금 기준 상위 10명 승객 정보 반환"""
    df = pd.read_csv(csv_path)
    top_10 = df.nlargest(10, 'Fare')
    
    result = []
    for idx, row in top_10.iterrows():
        rank = len(top_10) - list(top_10.index).index(idx)
        result.append({
            "rank": rank,
            "passengerId": int(row['PassengerId']),
            "name": row['Name'],
            "survived": "생존" if row['Survived'] == 1 else "사망",
            "pclass": f"{int(row['Pclass'])}등급",
            "sex": row['Sex'],
            "age": float(row['Age']) if pd.notna(row['Age']) else None,
            "fare": float(row['Fare']),
            "cabin": row['Cabin'] if pd.notna(row['Cabin']) else None
        })
    
    return result

@app.get("/")
async def root():
    return {"message": "Titanic Service API"}

@app.get("/top10")
async def get_top10():
    """요금 기준 상위 10명 승객 정보 반환"""
    try:
        passengers = get_top_10_passengers()
        return JSONResponse(content={
            "success": True,
            "data": passengers,
            "message": "요금 기준 상위 10명"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
