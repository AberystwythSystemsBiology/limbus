from app import create_app

app, _ = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
