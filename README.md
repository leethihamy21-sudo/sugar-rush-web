# Sugar Rush

## Chay local

Terminal 1:

```powershell
pnpm install
pnpm run dev
```

Terminal 2:

```powershell
python scene_1.py
```

Website: `http://localhost:8443`
Chatbot API: `http://localhost:5000/api/health`

## Deploy online voi GitHub va Render

GitHub luu ma nguon. Render chay Docker, Vite va Flask, nen website va chatbot dung chung mot domain.

1. Tao repository moi tren GitHub.
2. Trong thu muc project, chay:

```powershell
git init
git add .
git commit -m "Initial Sugar Rush website"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPOSITORY>.git
git push -u origin main
```

3. Vao Render, chon `New` -> `Blueprint` hoac `New Web Service`.
4. Ket noi repository GitHub nay.
5. Neu dung Blueprint, Render se doc `render.yaml`. Neu tao Web Service thu cong, chon `Docker`.
6. Deploy. Moi lan push len nhanh `main`, Render se tu dong build va deploy lai.

Render se tu dong doc bien moi truong `PORT`. Flask duoc chay bang Gunicorn trong `Dockerfile`, va cac trang da build gom:

- `/`
- `/shop.html`
- `/about-us.html`
- `/contact.html`
- `/cart.html`
- `/api/chat`

Khong dung GitHub Pages cho ban co chatbot Python: GitHub Pages chi chay file tinh va khong chay duoc Flask.
