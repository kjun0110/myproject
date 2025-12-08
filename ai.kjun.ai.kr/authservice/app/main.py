from fastapi import FastAPI, APIRouter
import uvicorn

app = FastAPI(
    title="Auth Service API",
    description="Auth Service API for the application",
    version="1.0.0",
)

# 서브 라우터 생성
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def auth_root():
    return {"message": "Auth Service"}


# 서브 라우터를 앱에 포함
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9011)

