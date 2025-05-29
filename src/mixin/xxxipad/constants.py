HOST: str = "127.0.0.1"
PORT: str = "9011"
PREFIX: str = "api"
URL = f"http://{HOST}:{PORT}"
if PREFIX:
    URL += f"/{PREFIX}"