DELETE_TMP_INTERVAL: int = 120
MESSAGE_QUEUE: dict = {
    "enable": True,
    "interval": 2.0
}
REDIS_HOST: str = "127.0.0.1"
REDIS_PORT: int = 6379
REDIS_PASSWORD: str = ""
REDIS_DB: int = 0
MYSQL_HOST: str = "127.0.0.1"
MYSQL_PORT: int = 3306
MYSQL_USER: str = "root"
MYSQL_PASSWORD: str = "123456"
MYSQL_DB: str = "weelink"
# Mongo DB
MONGO_URI: str = "mongodb://localhost:27017"
MONGO_DB_NAME: str = "WeeLink"