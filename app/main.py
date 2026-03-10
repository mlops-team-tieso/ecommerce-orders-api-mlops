import os
import time

import boto3
from fastapi import FastAPI
from mangum import Mangum

from app.api.orders import router as orders_router

_start_time = time.time()


def _check_dynamodb() -> dict:
    """Ping DynamoDB table to verify connectivity."""
    try:
        region = os.getenv("AWS_REGION", "us-east-1")
        table_name = os.getenv("ORDERS_TABLE_NAME", "orders")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table(table_name)
        table.table_status  # forces a DescribeTable call
        return {"dynamodb": "connected", "table": table_name, "region": region}
    except Exception as exc:
        return {"dynamodb": "error", "detail": str(exc)}


def create_app() -> FastAPI:
    app = FastAPI(title="Orders Service")

    @app.get("/", tags=["health"])
    def health_check():
        uptime_seconds = round(time.time() - _start_time, 2)
        db_status = _check_dynamodb()
        healthy = db_status.get("dynamodb") == "connected"

        return {
            "status": "healthy" if healthy else "degraded",
            "service": "orders-api",
            "version": os.getenv("IMAGE_TAG", "local"),
            "environment": os.getenv("ENV", "development"),
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "uptime_seconds": uptime_seconds,
            "dependencies": {
                "dynamodb": db_status,
                "products_service": os.getenv("PRODUCTS_SERVICE_URL", "not configured"),
            },
        }

    app.include_router(orders_router, prefix="/orders", tags=["orders"])
    return app


app = create_app()

# Lambda handler expected by the AWS base image / Dockerfile (app.main.handler)
handler = Mangum(app)
