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
COPY final_scene.xlsx ./
COPY scripts/export_data.py ./scripts/export_data.py
# Xuất xlsx -> JSON ngay lúc build: runtime chỉ đọc JSON (~ms), khỏi nạp openpyxl khi cold start
RUN python scripts/export_data.py final_scene.xlsx final_scene.json && rm -rf final_scene.xlsx scripts
COPY --from=frontend /app/dist ./dist
COPY scene_1.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --timeout 60 --preload scene_1:app"]