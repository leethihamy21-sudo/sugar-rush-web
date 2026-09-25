FROM node:22-slim AS frontend

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=frontend /app/dist ./dist
COPY scene_1.py ./
COPY final_scene.xlsx ./

ENV PYTHONUNBUFFERED=1
EXPOSE 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 scene_1:app"]
# (Phần trên giữ nguyên các lệnh build frontend và python của bạn)

# Lệnh khởi động cuối cùng để Render không bị Timeout
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "scene_1:app"]