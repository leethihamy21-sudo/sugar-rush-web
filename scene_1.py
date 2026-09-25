import os
import re
import unicodedata
from difflib import SequenceMatcher
import pandas as pd
from flask import Flask, jsonify, render_template, request

# Khởi tạo Flask
app = Flask(__name__)

# ============================================================
# 1. ĐỌC VÀ XỬ LÝ DỮ LIỆU TỪ FILE EXCEL (Chỉ đọc 1 lần khi khởi động)
# ============================================================
file_name = "final_scene.xlsx"

if not os.path.exists(file_name):
  raise FileNotFoundError(
      f"Không tìm thấy file '{file_name}' trong thư mục hiện tại."
  )

df = pd.read_excel(file_name, sheet_name="Chatbot Sugar Rush")
df.columns = [str(col).strip() for col in df.columns]
required_columns = ["Entities", "Intents", "Training", "Responses"]
df = df[required_columns].dropna(subset=["Intents"]).reset_index(drop=True)


# ============================================================
# 2. CÁC HÀM XỬ LÝ TIẾNG VIỆT VÀ KHỚP CÂU HỎI
# ============================================================
def normalize(text):
  if pd.isna(text):
    return ""
  text = str(text).lower().strip()
  text = text.replace("đ", "d")
  text = unicodedata.normalize("NFD", text)
  text = "".join(char for char in text if unicodedata.category(char) != "Mn")
  text = re.sub(r"[^a-z0-9\s]", " ", text)
  text = re.sub(r"\s+", " ", text).strip()
  return text


def cell_to_text(value):
  if pd.isna(value):
    return ""
  text = str(value)
  text = text.replace("\\n", "\n").replace("\r\n", "\n")
  return text.strip()


def extract_entity_keywords(entity_text):
  entity_text = cell_to_text(entity_text)
  lines = [line.strip() for line in entity_text.split("\n") if line.strip()]
  keywords = []
  for line in lines:
    if ":" in line:
      _, keyword_part = line.split(":", 1)
      for item in keyword_part.replace(";", ",").split(","):
        if normalize(item):
          keywords.append(normalize(item))
    else:
      for item in line.replace(";", ",").split(","):
        if normalize(item):
          keywords.append(normalize(item))
  return list(dict.fromkeys([k for k in keywords if k]))


def split_lines(value):
  return [line.strip() for line in cell_to_text(value).split("\n") if line.strip()]


# Lưu trữ dữ liệu ánh xạ Intent
intent_data = {}
for _, row in df.iterrows():
  intent = str(row["Intents"]).strip()
  intent_data[intent] = {
      "keywords": extract_entity_keywords(row["Entities"]),
      "training": [normalize(line) for line in split_lines(row["Training"])],
      "responses": cell_to_text(row["Responses"]),
  }


# ============================================================
# 3. NHẬN DIỆN Ý ĐỊNH VÀ LỌC CÂU TRẢ LỜI CỤ THỂ
# ============================================================
def detect_intent(user_text):
  text = normalize(user_text)

  service_keywords = {
      "iShip": ["ship", "phi ship", "gia ship", "giao hang", "van chuyen"],
      "iThanhtoan": [
          "thanh toan",
          "chuyen khoan",
          "tien mat",
          "cod",
          "qr",
      ],
      "iHoantrahang": ["doi tra", "tra hang", "hoan tien", "hoan tra"],
      "iHuydon": ["huy don", "doi y khong mua"],
      "iDathang": ["dat hang", "chot don", "len don"],
      "iGiamgia": ["giam gia", "uu dai", "khuyen mai"],
      "iHansudung": ["han su dung", "pao", "mo nap"],
      "iBaoquan": ["bao quan", "tu lanh", "nang"],
      "iKhieunai": ["khieu nai", "thai do", "nhan vien"],
      "iHieuqua": ["hieu qua", "bao lau", "tac dung"],
      "iChaohoi": ["chao", "hi", "hello", "shop oi", "ban oi", "alo"],
      "iLoichaotambiet": ["cam on", "thanks", "tam biet"],
  }

  for intent_name, kws in service_keywords.items():
    for kw in kws:
      if kw in text:
        if intent_name in intent_data:
          return intent_name

  best_intent = None
  best_score = 0

  for intent, data in intent_data.items():
    score = 0
    for tr in data["training"]:
      if tr and (tr in text or text in tr):
        score += 15
      elif SequenceMatcher(None, text, tr).ratio() >= 0.65:
        score += 8

    for kw in data["keywords"]:
      if kw and kw in text:
        score += 6

    if score > best_score:
      best_score = score
      best_intent = intent

  if best_score >= 6:
    return best_intent

  return None


def filter_specific_response(user_text, full_response):
  text = normalize(user_text)

  if "." not in full_response and len(full_response) < 80:
    return full_response

  sentences = [s.strip() for s in full_response.split(".") if s.strip()]

  is_asking_price = any(
      w in text for w in ["gia", "bao nhieu tien", "tien", "chi phí", "vnd", "đ"]
  )
  is_asking_capacity = any(
      w in text for w in ["dung tich", "ml", "gram", "bao nhieu ml", "chai"]
  )
  is_asking_usage = any(
      w in text
      for w in ["cach dung", "su dung", "dung the nao", "dung luc nao", "dung"]
  )
  is_asking_ingredient = any(w in text for w in ["thanh phan", "chiết xuất"])
  is_asking_benefit = any(
      w in text for w in ["cong dung", "tac dung", "giup gi", "lam gi"]
  )

  matched_sentences = []
  for s in sentences:
    s_lower = s.lower()
    if is_asking_price and (
        "gia" in s_lower or "đ" in s_lower or "vnd" in s_lower or "tiền" in s_lower
    ):
      matched_sentences.append(s)
    elif is_asking_capacity and ("ml" in s_lower or "chai" in s_lower):
      matched_sentences.append(s)
    elif is_asking_usage and (
        "dung" in s_lower or "su dung" in s_lower or "routine" in s_lower
    ):
      matched_sentences.append(s)
    elif is_asking_ingredient and ("thành phần" in s_lower or "chiết xuất" in s_lower):
      matched_sentences.append(s)
    elif is_asking_benefit and (
        "công dụng" in s_lower
        or "làm sạch" in s_lower
        or "cân bằng" in s_lower
        or "làm dịu" in s_lower
    ):
      matched_sentences.append(s)

  if matched_sentences:
    return ". ".join(matched_sentences) + "."

  return full_response


# ============================================================
# 4. ROUTE FLASK
# ============================================================
@app.route("/")
def home():
  return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
  user_text = request.json.get("message", "")
  intent = detect_intent(user_text)

  if intent and intent in intent_data:
    raw_response = intent_data[intent]["responses"]
    filtered_response = filter_specific_response(user_text, raw_response)
    reply = filtered_response.replace("\n", "<br>")
  else:
    reply = (
        "Dạ em chưa hiểu rõ ý của anh/chị lắm. Anh/chị có thể hỏi cụ thể hơn về"
        " sản phẩm, giá bán, cách dùng, phí ship hoặc đặt hàng nhé ạ!"
    )

  return jsonify({"reply": reply})


if __name__ == "__main__":
  app.run(debug=True, port=5000)