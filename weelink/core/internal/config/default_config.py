
VERSION = "3.5.13"

# 默认配置
DEFAULT_CONFIG = {
    # Redis
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    # MongoDB
    "MONGO_URI": "mongodb://localhost:27017",
    "MONGO_DB_NAME": "WeeLink",
    # Dashboard
    "DASHBOARD_HOST": "127.0.0.1",
    "DASHBOARD_PORT": 7070,
    "DASHBOARD_USERNAME": "weelink",
    "DASHBOARD_PASSWORD": "123456",
    "DASHBOARD_LOGLEVEL": "info",
    # Fastapi
    "BACKEND_CORS_CREDENTIALS": True,
    "BACKEND_CORS_ORIGINS": [
        "http://localhost:5173"
    ],
    "BACKEND_CORS_METHODS": [
        "*"
    ],
    "BACKEND_CORS_HEADERS": [
        "*"
    ],
    # Internal
    "inactive_plugins": [],
    "inactive_middlewares": []
}
