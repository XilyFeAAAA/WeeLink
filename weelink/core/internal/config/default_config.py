
VERSION = "3.5.13"

# 默认配置
DEFAULT_CONFIG = {
    "DELETE_TMP_INTERVAL": 120,
    "MESSAGE_QUEUE": {
        "enable": True,
        "interval": 2.0
    },
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_PORT": 3306,
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "123456",
    "MYSQL_DB": "weelink",
    # Mongo DB
    "MONGO_URI": "mongodb://localhost:27017",
    "MONGO_DB_NAME": "WeeLink",
}
