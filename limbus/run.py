import os
from app import create_app

# Initialised using the env variables set in Dockerfile
flask_config = os.getenv("FLASK_CONFIG")

app = create_app(flask_config)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
