from fastapi import FastAPI
from mangum import Mangum

from app.api.orders import router as orders_router


def create_app() -> FastAPI:
    app = FastAPI(title="Orders Service")
    app.include_router(orders_router, prefix="/orders", tags=["orders"])
    return app


app = create_app()

# Lambda handler expected by the AWS base image / Dockerfile (app.main.handler)
handler = Mangum(app)

