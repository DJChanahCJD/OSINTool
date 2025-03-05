from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors_middleware(app: FastAPI):
    """配置 CORS 中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )