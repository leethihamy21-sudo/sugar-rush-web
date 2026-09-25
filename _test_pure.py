import re, unicodedata
from difflib import SequenceMatcher
from functools import lru_cache
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
      print(f"[chatbot] WARNING: thieu ca {JSON_PATH} va {XLSX_PATH}, chay voi du lieu rong.")
      return {}
  except Exception as exc:  # khong de crash worker gunicorn
    print(f"[chatbot] WARNING: khong nap duoc du lieu: {exc}")
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


intent_data = {}


# ============================================================
# 3. NHẬN DIỆN 3 NHÓM: SẢN PHẨM / LOẠI DA / LOẠI CÂU HỎI (+ CONTEXT)
# ============================================================
# -- Sản phẩm: map keyword (đã normalize) -> intent sản phẩm trong Excel.
#    Thứ tự list = độ ưu tiên khi 1 câu nhắc nhiều sản phẩm.
PRODUCT_KEYWORDS = [  # tuple (intent, [keywords]); sort cụm dài trước ở vòng lặp dưới
    ("iSuaruamat", ["sua rua mat", "srm", "sua rua" , "rua mat"]),
    ("iToner", ["toner", "nuoc can bang", "nuoc hoa hong"]),
    ("iSerum", ["serum phuc hoi", "serum"]),
    ("iKemduong", ["kem duong am", "kem duong"]),
    ("iKemduongmat", ["kem duong mat", "kem mat", "kem duong vung mat"]),
    ("iSapduongdem", ["sap duong dem", "mat na ngu", "sap dem"]),
    ("iTaytebaochet", ["tay te bao chet", "tay da chet", "bha", "aha"]),
    ("iVitaminC", ["vitamin c", "vit c", "vc"]),
    ("iCombo", ["combo 4 buoc", "combo 4", "ca bo", "full bo", "tron bo",
                "combo 8", "combo", "bo skincare", "set"]),
    ("iCachdungcombo", ["thu tu dung ca bo", "cach dung combo", "dung combo"]),
    ("i8sanpham", ["bo 8 san pham", "full bo 8 mon", "8 san pham", "8 mon"]),
    ("iConhang", ["con hang", "con khong", "het hang"]),
]
for _, _kws in PRODUCT_KEYWORDS:
  _kws.sort(key=len, reverse=True)

SKIN_KEYWORDS = ["da thuong", "da nhay cam", "da hon hop",
                 "da kho", "da de noi mun", "da mun", "da dau"]

# -- Loại câu hỏi. QUAN TRỌNG: check theo thứ tự ưu tiên để tránh nhầm
#    "gia ship" -> ship chứ không phải giá sản phẩm.
#    Keyword đã normalize (không dấu). Keyword <=2 ký tự khớp nguyên từ
#    (xem _contains_kw) nên "k", "g", "hi" lẻ không ăn bậy.
QUESTION_PRIORITY = [
    ("ship", ["gia ship", "phi ship", "freeship", "free ship",
              "giao hang", "van chuyen", "ship"]),
    ("thanhtoan", ["thanh toan", "chuyen khoan", "tien mat", "cod", "qr",
                    "vi dien tu", "momo", "zalopay", "bank"]),
    ("hoantrahang", ["doi tra", "tra hang", "hoan tien", "hoan tra"]),
    ("huydon", ["huy don", "khong mua", "khong co nhu cau"]),
    ("dathang", ["dat hang", "chot don", "len don", "lay combo", "em lay",
                 "em chot", "cho em dat", "em dat"]),
    ("giamgia", ["giam gia", "uu dai", "khuyen mai", "chuong trinh"]),
    ("hansudung", ["han su dung", "han bao lau", "khi nao het han",
                   "mo nap", "pao"]),
    ("baoquan", ["bao quan", "de o dau", "tu lanh", "tranh nang",
                 "anh nang truc tiep"]),
    ("khieunai", ["khieu nai", "thai do", "nhan vien", "chua tot",
                  "chua on", "phuc vu"]),
    ("hieuqua", ["sau bao lau", "khi nao dep da", "bao lau", "hieu qua",
                 "khi nao", "tac dung"]),
    ("conhang", ["con hang", "con khong", "het hang"]),
    ("loaida", ["da thuong", "da nhay cam", "da hon hop", "da kho",
                "da de noi mun", "da mun", "da dau", "loai da"]),
    ("tuvan", ["tu van", "chon san pham nao", "muon hoi", "muon biet",
               "nen chon", "nen dung", "khong biet nen"]),
    ("gia", ["bao nhieu tien", "gia bao nhieu", "gia", "tien", "vnd",
             "dong", "chi phi", "k "]),
    ("dungtich", ["dung tich", "bao nhieu ml", "ml", "gram", "chai",
                  "lo", "hu", "tuyp"]),
    ("cachdung", ["cach dung", "dung the nao", "dung luc nao", "su dung",
                  "thoa", "boi", "thu tu dung", "routine", "sau buoc",
                  "truoc buoc", "moi ngay", "buoi sang", "buoi toi"]),
    ("thanhphan", ["thanh phan", "chiet xuat", "chiet suat"]),
    ("congdung", ["cong dung", "co tac dung gi", "co cong dung gi",
                  "giup gi", "lam gi", "tac dung", "cong dung"]),
    ("chaohoi", ["shop oi", "ban oi", "hello", "chao", "alo", "hi"]),
    ("tambiet", ["cam on", "thanks", "tam biet", "cam on shop"]),
]

# Regex kiểm chứng sau khi keyword khớp chuỗi con: tránh keyword chung
# ("gia", "tien", "bao lau", "khi nao") ăn nhầm ngữ cảnh khác.
# Nếu câu KHÔNG khớp regex mà chỉ khớp keyword chung -> coi như không hỏi ý đó.
QTYPE_REGEX_CHECK = {
    "gia": re.compile(r"gia|tien|vnd|dong|chi phi|\bk\b|\d"),
    "dungtich": re.compile(r"dung tich|ml|gram|chai|lo|hu|tuyp|\d"),
    "hansudung": re.compile(r"han|het han|mo nap|pao"),
    "hieuqua": re.compile(r"bao lau|hieu qua|khi nao|tac dung|tuan|thang|ngay"),
    "baoquan": re.compile(r"bao quan|tu lanh|nang|de o dau|tranh"),
    "huydon": re.compile(r"huy don|khong mua|khong co nhu cau|doi y"),
}

# Map question_type -> intent dịch vụ (khi không gắn với sản phẩm cụ thể).
QUESTION_TO_SERVICE_INTENT = {
    "ship": "iShip",
    "thanhtoan": "iThanhtoan",
    "hoantrahang": "iHoantrahang",
    "huydon": "iHuydon",
    "dathang": "iDathang",
    "giamgia": "iGiamgia",
    "hansudung": "iHansudung",
    "baoquan": "iBaoquan",
    "khieunai": "iKhieunai",
    "hieuqua": "iHieuqua",
    "conhang": "iConhang",
    "loaida": "iLoaida",
    "tuvan": "iTuvan",
    "chaohoi": "iChaohoi",
    "tambiet": "iLoichaotambiet",
}


def _contains_kw(text, kw):
  # Keyword ngắn (<=2 ký tự: hi, qr, ml...) phải khớp nguyên từ,
  # còn lại khớp chuỗi con. Tránh "hi" ăn mất "khi", "g" ăn lung tung.
  if len(kw) <= 2:
    return kw in set(text.split())
  return kw in text


def detect_product(text):
  """Trả về intent sản phẩm (vd iSerum) hoặc None. text đã normalize."""
  for intent_name, kws in PRODUCT_KEYWORDS:
    if intent_name not in intent_data:
      continue
    for kw in kws:
      if _contains_kw(text, kw):
        return intent_name
  return None


def detect_skin_type(text):
  """Trả về True nếu câu nhắc tới loại da. text đã normalize."""
  return any(_contains_kw(text, kw) for kw in SKIN_KEYWORDS)


def detect_question_type(text):
  """Trả về question_type theo bảng ưu tiên, hoặc None. text đã normalize."""
  for qtype, kws in QUESTION_PRIORITY:
    matched = False
    for kw in kws:
      if _contains_kw(text, kw):
        matched = True
        break
    if not matched:
      continue
    # Keyword chung (gia/tien/bao lau...) phải qua regex kiểm chứng ngữ cảnh.
    check = QTYPE_REGEX_CHECK.get(qtype)
    if check is not None and not check.search(text):
      continue
    return qtype
  return None


# ============================================================
# 4. DETECT INTENT THEO ĐÚNG THỨ TỰ ƯU TIÊN (Bước 4)
# ============================================================
# Dịch vụ / Loại da / Sản phẩm đều suy từ cùng một text, nhưng thứ tự
# quyết định: service > skin > product > keyword/training fallback.
def detect_intent(user_text):
  text = normalize(user_text)
  if not text:
    return None

  qtype = detect_question_type(text)
  product = detect_product(text)
  has_skin = detect_skin_type(text)

  # Ưu tiên 1: intent dịch vụ. "gia ship" đã map -> ship ở bảng ưu tiên
  # nên không bao giờ rớt nhầm sang giá sản phẩm.
  if qtype in QUESTION_TO_SERVICE_INTENT:
    svc = QUESTION_TO_SERVICE_INTENT[qtype]
    if svc in intent_data:
      return svc

  # Ưu tiên 2: loại da.
  if qtype == "loaida" or (has_skin and qtype in (None, "tuvan")):
    if "iLoaida" in intent_data:
      return "iLoaida"

  # Ưu tiên 3: sản phẩm cụ thể.
  if product:
    return product

  # Ưu tiên 4 (fallback): chấm điểm Entities + Training.
  best, best_score = None, 0
  for intent, data in intent_data.items():
    score = 0
    for kw in data["keywords"]:
      if kw and _contains_kw(text, kw):
        score += 2 if len(kw) <= 2 else 6
    for tr in data["training"]:
      if not tr:
        continue
      if tr in text or text in tr:
        score += 15
        break
    if score > best_score:
      best_score = score
      best = intent
    if best_score >= 21:
      return best
  if best_score >= 2:
    # Fuzzy chỉ khi khớp cứng thất bại; giới hạn lệch độ dài cho rẻ.
    fuzzy_intent, fuzzy_score = None, 0.0
    for intent, data in intent_data.items():
      for tr in data["training"]:
        if not tr or abs(len(text) - len(tr)) > 30:
          continue
        r = SequenceMatcher(None, text, tr).ratio()
        if r > fuzzy_score:
          fuzzy_score, fuzzy_intent = r, intent
          if r >= 0.85:
            return fuzzy_intent
    if fuzzy_score >= 0.5 and (fuzzy_score * 10) > best_score:
      return fuzzy_intent
    return best

  # Điểm quá thấp (< 2): thử fuzzy lần cuối, không được -> None.
  fuzzy_intent, fuzzy_score = None, 0.0
  for intent, data in intent_data.items():
    for tr in data["training"]:
      if not tr or abs(len(text) - len(tr)) > 30:
        continue
      r = SequenceMatcher(None, text, tr).ratio()
      if r > fuzzy_score:
        fuzzy_score, fuzzy_intent = r, intent
        if r >= 0.85:
          return fuzzy_intent
  return fuzzy_intent if fuzzy_score >= 0.5 else None


def filter_specific_response(user_text, full_response):
  """Hàm lọc mạnh mẽ: Tách câu và loại bỏ hoàn toàn các câu lạc đề

  dựa trên ý định thực tế của người dùng.
  """
  text = normalize(user_text)
  if not full_response:
    return ""

  # Tách phản hồi thành từng câu dựa vào dấu chấm, dấu phẩy ngắt dòng hoặc ký tự xuống dòng
  raw_sentences = re.split(r"[\.\n]", full_response)
  sentences = [s.strip() for s in raw_sentences if s.strip()]

  if len(sentences) <= 1:
    return full_response

  # Phân tích ý định người dùng cực kỳ cụ thể
  asking_usage = any(
      w in text
      for w in [
          "cach dung",
          "su dung",
          "dung the nao",
          "dung luc nao",
          "dung",
          "thoa",
          "boi",
      ]
  )
  asking_benefit = any(
      w in text
      for w in [
          "cong dung",
          "tac dung",
          "giup gi",
          "lam gi",
          "co tac dung gi",
          "co cong dung gi",
      ]
  )
  asking_price = any(
      w in text for w in ["gia", "bao nhieu tien", "tien", "chi phí", "vnd", "đ"]
  )
  asking_capacity = any(
      w in text for w in ["dung tich", "ml", "gram", "bao nhieu ml", "chai"]
  )

  filtered_list = []

  for s in sentences:
    s_lower = s.lower()

    if asking_usage and not asking_benefit:
      # Nếu hỏi cách dùng: chỉ lấy câu có chứa thông tin sử dụng/sau bước/trước bước và TUYỆT ĐỐI KHÔNG chứa từ khóa định nghĩa công dụng
      has_usage_kw = any(
          w in s_lower
          for w in [
              "dùng",
              "sử dụng",
              "thoa",
              "bôi",
              "sau bước",
              "trước bước",
              "routine",
              "mỗi ngày",
              "ngày",
              "sáng",
              "tối",
              "bước",
          ]
      )
      has_benefit_kw = any(
          w in s_lower
          for w in [
              "công dụng",
              "tác dụng",
              "cân bằng",
              "làm dịu",
              "thu nhỏ",
              "giúp",
          ]
      )

      if has_usage_kw and not has_benefit_kw:
        filtered_list.append(s)

    elif asking_benefit and not asking_usage:
      # Nếu hỏi công dụng: chỉ lấy câu chứa từ khóa công dụng và không chứa thông tin cách dùng
      has_benefit_kw = any(
          w in s_lower
          for w in [
              "công dụng",
              "tác dụng",
              "giúp",
              "làm sạch",
              "cân bằng",
              "làm dịu",
              "dưỡng",
              "cấp ẩm",
              "hỗ trợ",
          ]
      )
      has_usage_kw = any(
          w in s_lower for w in ["dùng sau", "dùng trước", "routine", "sử dụng"]
      )

      if has_benefit_kw and not has_usage_kw:
        filtered_list.append(s)

    elif asking_price:
      if any(w in s_lower for w in ["giá", "đ", "vnd", "tiền", "đồng", "vnđ"]):
        filtered_list.append(s)

    elif asking_capacity:
      if any(w in s_lower for w in ["ml", "gram", "g", "dung tích", "chai", "lọ"]):
        filtered_list.append(s)

  # Nếu lọc thành công các câu chuyên biệt, trả về các câu đó
  if filtered_list:
    result = ". ".join(filtered_list)
    if not result.endswith("."):
      result += "."
    return result

  # Trường hợp người dùng hỏi chung chung hoặc không khớp bộ lọc sâu,
  # nếu hỏi cách dùng mà không tìm được câu thuần cách dùng, ưu tiên trả về câu đầu tiên chứa từ "dùng"/"sử dụng"
  if asking_usage:
    for s in sentences:
      if any(w in s.lower() for w in ["dùng", "sử dụng", "thoa", "bôi"]):
        return s + ("." if not s.endswith(".") else "")

  return sentences[0] + "." if sentences else full_response


# ============================================================
# 5. LỌC CÂU TRẢ LỜI BẰNG REGEX (Bước 5) - không tách ý trong Excel
# ============================================================
# Responses trong Excel giữ nguyên 1 đoạn dài. Hàm này tách thành từng
# "đơn vị thông tin" (câu / mệnh đề sau dấu . ; \n, GIỮ NGUYÊN dấu chấm
# trong số như 150.000đ và 2-3 giọt) rồi chấm điểm từng đơn vị theo
# question_type, chỉ giữ đơn vị khớp ý khách hỏi.
_NUM_DOT = "\u0001"  # placeholder cho dấu chấm nằm trong số
_WS_RE = re.compile(r"\s+")

# Regex tìm trực tiếp dữ kiện (ưu tiên hơn keyword chung chung).
RE_PRICE = re.compile(r"\d[\d.]*\s*(?:000)?\s*(?:d|vnd|dong|k\b)")
RE_CAPACITY = re.compile(r"\d+\s*(?:ml|g\b|gram)\b|\b(?:chai|lo|hu|tuyp)\b")
RE_TIME = re.compile(r"\d+\s*(?:ngay|tuan|thang|nam)\b|2\s*lan|moi ngay")
RE_DOSAGE = re.compile(r"\d+\s*(?:giot|lan|la)\b|\d+\s*-\s*\d+\s*(?:giot|lan)")
RE_ROUTINE = re.compile(r"sau buoc|truoc buoc|routine|buoc\s*\d|buoi\s*(?:sang|toi)")
RE_INGREDIENT = re.compile(r"thanh phan|chiet xuat|chiet suat|vitamin|niacinamide|bha|aha")

# Từ khóa chấm điểm theo từng question_type (đã normalize, không dấu).
QTYPE_KEYWORDS = {
    "gia": (["gia", "tien", "vnd", "dong", "000"], RE_PRICE, 4),
    "dungtich": (["dung tich", "ml", "gram", "chai", "lo", "hu", "tuyp"], RE_CAPACITY, 4),
    "cachdung": (["cach dung", "su dung", "thoa", "boi", "sau buoc", "truoc buoc",
                 "routine", "moi ngay", "lan/ngay", "lan", "giot",
                 "buoi", "thay the", "buoc cuoi"], RE_DOSAGE, 2),
    "thanhphan": (["thanh phan", "chiet xuat", "chua"], RE_INGREDIENT, 3),
    "congdung": (["cong dung", "tac dung", "giup", "lam sach", "can bang",
                 "lam diu", "duong", "cap am", "ho tro", "phuc hoi",
                 "thu nho", "sang da", "mo tham"], None, 2),
    "hansudung": (["han", "pao", "mo nap", "thang", "nam", "san xuat"], RE_TIME, 3),
    "hieuqua": (["tuan", "ngay", "thang", "hieu qua", "tac dung", "cam nhan"], RE_TIME, 3),
    "baoquan": (["bao quan", "kho rao", "thoang mat", "tranh", "nang", "tu lanh",
                "nap", "anh sang"], None, 2),
    "ship": (["ship", "giao", "van chuyen", "freeship", "cod", "ngay", "khu vuc"], None, 2),
}

# Đơn vị chứa từ của ý KHÁC (không phải ý đang hỏi) -> trừ điểm để không
# lọt chung. Vd hỏi cách dùng mà đơn vị toàn nói công dụng -> loại.
QTYPE_EXCLUDE = {
    "gia": ["dung", "thanh phan", "cong dung", "tac dung", "routine", "buoc"],
    "dungtich": ["dung", "su dung", "thanh phan", "cong dung", "tac dung"],
    "cachdung": ["thanh phan", "cong dung", "tac dung", "gia", "000"],
    "thanhphan": ["gia", "000", "dung", "su dung", "cong dung", "routine"],
    "congdung": ["gia", "000", "dung", "su dung", "thanh phan", "routine"],
}

# Câu mang nghĩa phủ định của ý đang hỏi -> trừ điểm (vd hỏi cách dùng
# nhưng câu nói "không cần kem dưỡng").
NEG_RE = re.compile(r"\b(khong|chua|dung nen|tra |loai bo)\b")

# Nhãn "Thành phần" mà câu sau toàn từ cách dùng (dung/thoa/routine...)
# hoặc ngược lại -> KHÔNG gộp, tránh dính 2 ý như "Dùng 2 lần/ngày: Thành phần".
_LABEL_QTYPE = [
    ("thanh phan", "thanhphan"),
    ("chiet xuat", "thanhphan"),
    ("cong dung", "congdung"),
    ("tac dung", "congdung"),
    ("cach dung", "cachdung"),
    ("su dung", "cachdung"),
    ("gia", "gia"),
    ("dung tich", "dungtich"),
]


def _clashes_with_label(label, line):
  label_ns, line_ns = normalize(label), normalize(line)
  label_q = next((q for kw, q in _LABEL_QTYPE if kw in label_ns), None)
  if label_q is None:
    return False
  # Câu sau chứa từ khóa ý khác (theo QTYPE_EXCLUDE của ý nhãn) -> xung đột.
  return any(ex in line_ns for ex in QTYPE_EXCLUDE.get(label_q, []))


# Câu hỏi tu từ trong Responses (vd "Bạn muốn tư vấn combo nào a?")
# không phải thông tin -> trừ điểm để khỏi lọt vào kết quả lọc.
RHETORICAL_RE = re.compile(r"ban muon|nao\s+a\??|\?$")


def _split_units(full_response):
  text = cell_to_text(full_response)
  # B1: che dấu chấm trong số (150.000đ, 2.5ml) để không bị chẻ đôi.
  text = re.sub(r"(?<=\d)[.](?=\d)", _NUM_DOT, text)
  # B2: tách theo xuống dòng / dấu ; / dấu chấm câu / dấu hai chấm SAU NHÃN.
  # Chỉ tách tại ':' khi sau nó là chữ HOA (nhãn thật: "Thành phần: Các...").
  # Dấu ':' đứng TRƯỚC nhãn ("...ngày: Thành phần") hoặc sau chữ thường
  # ("Dùng 2 lần/ngày: ...") KHÔNG tách — đó là nội dung liền mạch của cùng
  # 1 ý, tách ra sẽ tạo nhãn treo rồi gộp nhầm sang ý khác.
  # -> Biến "...ngày: Thành phần: Các..." thành "...ngày. Thành phần: Các..."
  # (chấm câu tách 2 ý, hai chấm giữ nhãn với nội dung). Khớp trên text GỐC
  # (còn dấu) nên pattern phải gồm cả dạng có dấu.
  text = re.sub(r":\s*(?=(?:thành phần|công dụng|tác dụng|giá|dung tích|cách dùng))",
                ". ", text, flags=re.IGNORECASE)
  raw = re.split(r"[\n;]+|(?<=[.!?])\s+|(?<=\D):\s*(?=[A-Z\u00C0-\u1EF9])", text)
  # B3: gộp nhãn ngắn ("Thành phần", "Công dụng của Serum là") vào nội dung sau nó.
  parts = []
  for line in raw:
    line = line.strip(" -").replace(_NUM_DOT, ".")
    line = _WS_RE.sub(" ", line).strip(" -.,")
    if len(line) >= 4:
      parts.append(line)
  units = []
  for idx, line in enumerate(parts):
    ns = normalize(line)
    is_label = (len(line) < 30 and not RE_PRICE.search(ns)
                and not RE_DOSAGE.search(ns) and not RE_CAPACITY.search(ns))
    if is_label and units and len(units[-1]) < 30:
      units[-1] = f"{units[-1]}: {line}"  # 2 nhãn liên tiếp -> gộp
    elif is_label:
      # Nhãn treo ("Thành phần", "Công dụng của Serum là"): chỉ gộp với câu
      # SAU nếu câu sau cùng ý (không chứa từ khóa của ý khác). Nếu câu sau
      # thuộc ý khác (vd nhãn "Thành phần" mà câu sau nói cách dùng) thì
      # giữ nhãn đứng riêng để khỏi dính 2 ý vào 1 unit.
      nxt = parts[idx + 1] if idx + 1 < len(parts) else ""
      units.append(line + " <MERGE_NEXT>" + nxt)
    elif units and "<MERGE_NEXT>" in units[-1]:
      label, _, expected_next = units[-1].partition("<MERGE_NEXT>")
      if line == expected_next and not _clashes_with_label(label, line):
        units[-1] = f"{label}: {line}"
      else:
        units[-1] = label  # không gộp: nhãn đứng riêng, câu sau đứng riêng
        units.append(line)
    else:
      units.append(line)
  return [u.replace(" <MERGE_NEXT>", "").strip() for u in units if len(u.replace(" <MERGE_NEXT>", "").strip()) >= 4]


def _score_unit(ns, qtype):
  kws, rx, w = QTYPE_KEYWORDS.get(qtype, ([], None, 0))
  score = 0
  for kw in kws:
    if kw in ns:
      score += w
  if rx and rx.search(ns):
    score += w + 2  # regex trúng dữ kiện thật -> cộng nặng
  for ex in QTYPE_EXCLUDE.get(qtype, []):
    if ex in ns:
      score -= 2  # lẫn ý khác -> trừ
  if NEG_RE.search(ns):
    score -= 3
  if RHETORICAL_RE.search(ns):
    score -= 4
  return score


def choose_response(question_type, full_response, intent=None, max_units=2):
  """Lọc Responses theo question_type.

  CHỈ lọc khi intent là sản phẩm/cách dùng combo (Responses chứa nhiều ý).
  Intent dịch vụ / loại da / combo-liệt-kê / còn hàng: trả nguyên kịch bản
  Excel vì mỗi câu trong đó đều là thông tin cần thiết.
  """
  if not full_response:
    return ""
  if question_type not in QTYPE_KEYWORDS:
    return full_response.strip()
  if intent is not None and intent not in PRODUCT_INTENTS:
    return full_response.strip()
  units = _split_units(full_response)
  if len(units) <= 1:
    return full_response.strip()
  scored = [(u, _score_unit(normalize(u), question_type)) for u in units]
  best = max(s for _, s in scored)
  if best <= 0:
    return units[0]  # không đơn vị nào khớp -> câu đầu, không trả cả đoạn
  kept = [u for u, s in scored if s >= max(2, best - 2)][:max_units]
  return ". ".join(kept) + "."


# Intent nào thì Responses chứa nhiều ý cần lọc (giá/dung tích/cách dùng...).
# Các intent còn lại (dịch vụ, loại da, combo, còn hàng...) trả nguyên văn.
PRODUCT_INTENTS = {
    "iSuaruamat", "iToner", "iSerum", "iKemduong", "iKemduongmat",
    "iSapduongdem", "iTaytebaochet", "iVitaminC", "iCachdungcombo",
}


# Giữ tên cũ để tương thích: suy question_type từ câu hỏi rồi gọi choose_response.
# (Hàm filter_specific_response cũ vẫn giữ nguyên bên dưới cho fallback.)
def filter_specific_response_v2(user_text, full_response, intent=None):
  return choose_response(detect_question_type(normalize(user_text)), full_response, intent)


