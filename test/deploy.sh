#!/bin/bash
# Sunucuda tek komutla deploy: kod cek, statik dogrula, imaj kur, eski container'i sakla, yenisini baslat, saglik kontrolu.
# Betikte parola veya token yoktur; gizli degerler sunucudaki config.json icindedir.
set -euo pipefail

NAME="oryantasyon"
PORT=5123
RETRIES=20

git pull
echo "Surum: $(cat version.txt)"

# Statik dogrulama imajdan ONCE calisir; canli DB'ye yazan test paketi burada calistirilmaz.
python3 test/calistir.py --statik

docker build -t "$NAME" .

if docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
    docker rm -f "${NAME}_geri_donus" 2>/dev/null || true
    docker stop "$NAME"
    docker rename "$NAME" "${NAME}_geri_donus"
fi

docker compose up -d

for attempt in $(seq 1 "$RETRIES"); do
    if curl -fsS -o /dev/null "http://localhost:${PORT}/auth/login"; then
        echo "Saglik kontrolu basarili"
        docker rm -f "${NAME}_geri_donus" 2>/dev/null || true
        exit 0
    fi
    sleep 3
done

echo "Saglik kontrolu BASARISIZ. Son loglar:"
docker logs --tail 30 "$NAME" || true
echo "Geri donus: docker rm -f $NAME && docker rename ${NAME}_geri_donus $NAME && docker start $NAME"
exit 1
