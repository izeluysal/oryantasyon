FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# gosu: root'tan uygulama kullanıcısına güvenli düşüş için (su/sudo yerine —
# sinyal iletimi ve PID 1 davranışı için tasarlanmış).
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/oryantasyonfiles /app/oryantasyongorseller

# Container root olarak çalışmaz: entrypoint volume sahipliğini onarır, sonra gosu ile bu kullanıcıya düşer.
RUN useradd --create-home --uid 10001 oryantasyonappuser \
    && chown -R oryantasyonappuser:oryantasyonappuser /app \
    && chmod +x /app/entrypoint.sh

EXPOSE 5123

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5123", "--workers", "2", "--timeout", "60", "application:app"]
