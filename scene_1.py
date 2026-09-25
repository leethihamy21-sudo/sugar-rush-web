import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache

from flask import Flask, jsonify, request, send_from_directory

# Flask phục vụ luôn frontend đã build (Vite -> dist/): 1 service duy nhất trên Render.
# static_folder=None để route /<path:path> bên dưới tự xử lý file + SPA fallback
# (tránh xung đột với static route mặc định của Flask).
app = Flask(__name__, static_folder=None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
XLSX_PATH = os.path.join(BASE_DIR, "final_scene.xlsx")
JSON_PATH = os.path.join(BASE_DIR, "final_scene.json")  # cache build-time (optional)
SHEET_NAME = "Chatbot Sugar Rush"


# ============================================================
# 1. NẠP DỮ LIỆU (JSON cache -> XLSX openpyxl). Không crash worker nếu thiếu file.
# ============================================================
def _rows_from_json():
  with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)
  rows = []
  for item in data if isinstance(data, list) else data.get("intents", []):
    if item.get("Intents"):
      rows.append(item)
  return rows


def _rows_from_xlsx():
  # openpyxl read-only: nhẹ hơn pandas+numpy rất nhiều (~5MB vs ~80MB).
  from openpyxl import load_workbook

  wb = load_workbook(XLSX_PATH, read_only=True, data_only=True)
  ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb.active
  header = [str(c.value).strip() if c.value is not None else "" for c in next(ws.iter_rows(min_row=1, max_row=1))]
  idx = {name: i for i, name in enumerate(header)}
  rows = []
  for r in ws.iter_rows(min_row=2, values_only=True):
    r = list(r) + [""] * (len(header) - len(r))  # hàng thiếu ô -> đệm rỗng
    try:
      intent = str(r[idx["Intents"]]).strip() if r[idx["Intents"]] is not None else ""
    except (KeyError, IndexError, TypeError):
      continue
    if not intent or intent.lower() == "nan":
      continue
    def _cell(name):
      try:
        return r[idx[name]]
      except (KeyError, IndexError, TypeError):
        return ""
    rows.append({
        "Entities": _cell("Entities"),
        "Intents": intent,
        "Training": _cell("Training"),
        "Responses": _cell("Responses"),
    })
  wb.close()
  return rows


# ============================================================
# 2. CÁC HÀM XỬ LÝ TIẾNG VIỆT & LỌC CÂU TRẢ LỜI
# ============================================================
@lru_cache(maxsize=4096)
def normalize(text):
  if text is None:
    return ""
  text = str(text).lower().strip()
  if not text:
    return ""
  text = text.replace("đ", "d")
  text = unicodedata.normalize("NFD", text)
  text = "".join(c for c in text if unicodedata.category(c) != "Mn")
  text = re.sub(r"[^a-z0-9\s]", " ", text)
  return re.sub(r"\s+", " ", text).strip()


def cell_to_text(value):
  if value is None:
    return ""
  try:
    import math
    if isinstance(value, float) and math.isnan(value):
      return ""
  except (ImportError, TypeError):
    pass
  return str(value).replace("\\n", "\n").replace("\r\n", "\n").strip()


def extract_entity_keywords(entity_text):
  lines = [ln.strip() for ln in cell_to_text(entity_text).split("\n") if ln.strip()]
  keywords = []
  for line in lines:
    part = line.split(":", 1)[1] if ":" in line else line
    for item in part.replace(";", ",").split(","):
      norm = normalize(item)
      if norm:
        keywords.append(norm)
  return list(dict.fromkeys(keywords))


def split_lines(value):
  return [line.strip() for line in cell_to_text(value).split("\n") if line.strip()]


def _build_intent_data():
  try:
    if os.path.exists(JSON_PATH):
      rows = _rows_from_json()
    elif os.path.exists(XLSX_PATH):
      rows = _rows_from_xlsx()
    else:
      print(f"[chatbot] WARNING: thiếu cả {JSON_PATH} và {XLSX_PATH}, chạy với dữ liệu rỗng.")
      return {}
  except Exception as exc:  # không để crash worker gunicorn
    print(f"[chatbot] WARNING: không nạp được dữ liệu: {exc}")
    return {}
  data = {}
  for row in rows:
    intent = str(row.get("Intents", "")).strip()
    if not intent:
      continue
    data[intent] = {
        "keywords": extract_entity_keywords(row.get("Entities")),
        "training": [t for t in (normalize(ln) for ln in split_lines(row.get("Training"))) if t],
        "responses": cell_to_text(row.get("Responses")),
    }
  print(f"[chatbot] loaded {len(data)} intents.")
  return data


intent_data = _build_intent_data()

# Bảng keyword dịch vụ: tra cứu nhanh, sort theo độ dài giảm dần để ưu tiên cụm dài.
SERVICE_KEYWORDS = {
    "iShip": ["phi ship", "gia ship", "giao hang", "van chuyen", "ship"],
    "iThanhtoan": ["thanh toan", "chuyen khoan", "tien mat", "cod", "qr"],
    "iHoantrahang": ["doi tra", "tra hang", "hoan tien", "hoan tra"],
    "iHuydon": ["huy don", "doi y khong mua"],
    "iDathang": ["dat hang", "chot don", "len don"],
    "iGiamgia": ["giam gia", "uu dai", "khuyen mai"],
    "iHansudung": ["han su dung", "mo nap", "pao"],
    "iBaoquan": ["bao quan", "tu lanh", "nang"],
    "iKhieunai": ["khieu nai", "thai do", "nhan vien"],
    "iHieuqua": ["hieu qua", "bao lau", "tac dung"],
    "iChaohoi": ["shop oi", "ban oi", "hello", "chao", "alo", "hi"],
    "iLoichaotambiet": ["cam on", "thanks", "tam biet"],
}
for _kws in SERVICE_KEYWORDS.values():
  _kws.sort(key=len, reverse=True)


def detect_intent(user_text):
  text = normalize(user_text)
  if not text:
    return None
  words = set(text.split())

  # Pass 1: keyword dịch vụ (rẻ nhất). Keyword <=2 ký tự phải khớp nguyên từ.
  for intent_name, kws in SERVICE_KEYWORDS.items():
    if intent_name not in intent_data:
      continue
    for kw in kws:
      if len(kw) <= 2:
        if kw in words:
          return intent_name
      elif kw in text:
        return intent_name

  # Pass 2: khớp chuỗi con training + keyword (rẻ), fuzzy chỉ khi cần (đắt).
  best_intent, best_score = None, 0
  for intent, data in intent_data.items():
    score = 0
    for kw in data["keywords"]:
      if kw and kw in text:
        score += 6
    for tr in data["training"]:
      if not tr:
        continue
      if tr in text or text in tr:
        score += 15
        break  # đủ chắc, khỏi quét tiếp training của intent này
    if score > best_score:
      best_score = score
      best_intent = intent
    if best_score >= 21:  # keyword + training khớp -> chốt sớm
      return best_intent
  if best_score >= 6:
    return best_intent

  # Pass 3 (đắt nhất): fuzzy chỉ chạy khi 2 pass trên thất bại.
  # Giới hạn độ lệch độ dài để tránh SequenceMatcher vô ích.
  best_intent, best_score = None, 0.0
  for intent, data in intent_data.items():
    for tr in data["training"]:
      if not tr or abs(len(text) - len(tr)) > 30:
        continue
      r = SequenceMatcher(None, text, tr).ratio()
      if r > best_score:
        best_score = r
        best_intent = intent
        if r >= 0.85:
          return best_intent
  return best_intent if best_score >= 0.65 else None


def filter_specific_response(user_text, full_response):
  if not full_response:
    return full_response
  if "." not in full_response and len(full_response) < 80:
    return full_response
  text = normalize(user_text)
  # Lưu ý: text đã normalize (không dấu) nên mọi keyword so sánh cũng phải không dấu.
  is_asking_price = ("gia" in text or "bao nhieu tien" in text or "tien" in text
                       or "chi phi" in text or "vnd" in text)
  is_asking_capacity = ("dung tich" in text or "ml" in text or "gram" in text or "chai" in text)
  is_asking_usage = "cach dung" in text or "su dung" in text or "dung" in text
  is_asking_ingredient = "thanh phan" in text or "chiet xuat" in text
  is_asking_benefit = ("cong dung" in text or "tac dung" in text or "giup gi" in text or "lam gi" in text)
  if not (is_asking_price or is_asking_capacity or is_asking_usage or is_asking_ingredient or is_asking_benefit):
    return full_response

  sentences = [s.strip() for s in full_response.split(".") if s.strip()]
  matched = []
  for s in sentences:
    ns = normalize(s)
    if is_asking_price and ("gia" in ns or "vnd" in ns or "tien" in ns or "d " in f"{ns} "):
      matched.append(s)
    elif is_asking_capacity and ("ml" in ns or "chai" in ns or "gram" in ns):
      matched.append(s)
    elif is_asking_usage and ("dung" in ns or "routine" in ns):
      matched.append(s)
    elif is_asking_ingredient and ("thanh phan" in ns or "chiet xuat" in ns):
      matched.append(s)
    elif is_asking_benefit and ("cong dung" in ns or "lam sach" in ns or "can bang" in ns or "lam diu" in ns):
      matched.append(s)
  return (". ".join(matched) + ".") if matched else full_response


# ============================================================
# 3. ROUTES: /api/* cho chatbot (khớp với vite proxy + frontend fetch),
#    /* còn lại phục vụ file tĩnh trong dist/ (1 domain duy nhất).
# ============================================================
@app.get("/api/health")
def api_health():
  return jsonify({"ok": True, "intents": len(intent_data)})


FALLBACK_REPLY = ("Dạ em chưa hiểu rõ ý của anh/chị lắm. Anh/chị có thể hỏi cụ thể hơn về"
                  " sản phẩm, giá bán, cách dùng, phí ship hoặc đặt hàng nhé ạ!")


@app.post("/api/chat")
@app.post("/chat")  # giữ tương thích với bản cũ / proxy cũ
def chat():
  data = request.get_json(silent=True) or {}
  user_text = str(data.get("message", ""))[:500]
  if not user_text.strip():
    return jsonify({"reply": FALLBACK_REPLY, "response": FALLBACK_REPLY})
  intent = detect_intent(user_text)
  if intent and intent in intent_data:
    reply = filter_specific_response(user_text, intent_data[intent]["responses"]).replace("\n", "<br>")
  else:
    reply = FALLBACK_REPLY
  # Trả cả 2 key để tương thích mọi bản frontend (data.reply / data.response).
  return jsonify({"reply": reply, "response": reply, "intent": intent})


@app.get("/")
def home():
  return send_from_directory(DIST_DIR, "index.html")


@app.get("/<path:path>")
def serve_dist(path):
  # /api đã được khai báo ở trên nên không lọt xuống đây.
  full = os.path.join(DIST_DIR, path)
  if os.path.isfile(full):
    return send_from_directory(DIST_DIR, path)
  # SPA fallback: /shop.html, /cart.html... là file thật nên đã return ở trên;
  # route lạ thì trả index.html.
  index = os.path.join(DIST_DIR, "index.html")
  if os.path.exists(index):
    return send_from_directory(DIST_DIR, "index.html")
  return jsonify({"ok": True, "intents": len(intent_data)})


if __name__ == "__main__":
  port = int(os.environ.get("PORT", "5000"))
  app.run(host="0.0.0.0", port=port)