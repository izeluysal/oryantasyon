"""Gunicorn giriş noktası: `application:app`."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug ortam değişkenine bağlıdır; üretimde APP_DEBUG tanımlanmaz.
    app.run(host="0.0.0.0", port=5123, debug=os.environ.get("APP_DEBUG") == "1")
