import os
import pandas as pd
import re
import random
import unicodedata
from difflib import SequenceMatcher

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================================
# 1. KIỂM TRA VÀ TẢI FILE EXCEL TRÊN THƯ MỤC VS CODE
# ============================================================

file_name = "final_scene.xlsx"
sheet_name = "Chatbot Sugar Rush"

if not os.path.exists(file_name):
    raise ValueError(f"Không tìm thấy file '{file_name}' trong thư mục hiện tại! Hãy đảm bảo bạn đã đặt file Excel cùng cấp với file Python này.")

# Đọc đúng sheet theo tên trong file
excel_file = pd.ExcelFile(file_name)

if sheet_name not in excel_file.sheet_names:
    raise ValueError(
        f"Không tìm thấy sheet '{sheet_name}'. "
        f"Các sheet hiện có trong file: {excel_file.sheet_names}"
    )

df = pd.read_excel(file_name, sheet_name=sheet_name)

# Chuẩn hóa tên cột, bỏ khoảng trắng thừa
df.columns = [str(col).strip() for col in df.columns]

required_columns = [
    "Entities",
    "Intents",
    "Training",
    "Responses"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        "File Excel đang thiếu cột: "
        + ", ".join(missing_columns)
    )

df = df[required_columns].dropna(
    subset=["Intents"]
).reset_index(drop=True)

print(f"Đã đọc file '{file_name}' thành công.")
print("Số dòng Intent:", len(df))


# ============================================================
# 2. CHUẨN HÓA TIẾNG VIỆT
# ============================================================

def normalize(text):
    """Chuyển chữ về dạng thường, bỏ dấu và ký tự đặc biệt."""
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()
    text = text.replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def cell_to_text(value):
    """Chuyển nội dung Excel thành chuỗi và xử lý xuống dòng."""
    if pd.isna(value):
        return ""

    text = str(value)
    text = text.replace("\\n", "\n")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text.strip()


# ============================================================
# 3. ĐỌC KEYWORD, TRAINING VÀ RESPONSE TỪ EXCEL
# ============================================================

def extract_entity_keywords(entity_text):
    """Đọc keyword từ cột Entities."""
    entity_text = cell_to_text(entity_text)
    lines = [
        line.strip()
        for line in entity_text.split("\n")
        if line.strip()
    ]

    keywords = []
    for line in lines[1:]:
        if ":" in line:
            label, keyword_part = line.split(":", 1)
            label = normalize(label)
            if label:
                keywords.append(label)

            keyword_part = keyword_part.replace(";", ",")
            for item in keyword_part.split(","):
                item = normalize(item)
                if item:
                    keywords.append(item)
        else:
            for item in line.replace(";", ",").split(","):
                item = normalize(item)
                if item:
                    keywords.append(item)

    unique_keywords = []
    for keyword in keywords:
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)

    return unique_keywords


def split_lines(value):
    """Tách các câu/ý trong ô Excel theo dòng."""
    text = cell_to_text(value)
    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


intent_data = {}

for _, row in df.iterrows():
    intent = str(row["Intents"]).strip()
    intent_data[intent] = {
        "entities_raw": cell_to_text(row["Entities"]),
        "keywords": extract_entity_keywords(row["Entities"]),
        "training": [
            normalize(line)
            for line in split_lines(row["Training"])
        ],
        "responses": split_lines(row["Responses"])
    }

if not intent_data:
    raise ValueError("Không đọc được Intent nào từ file Excel.")

print("Đã nạp", len(intent_data), "Intent vào chatbot.")


# ============================================================
# 4. NHẬN DIỆN SẢN PHẨM & LOẠI DA & LOẠI CÂU HỎI
# ============================================================

PRODUCT_KEYWORDS = {
    "sua_rua_mat": ["sữa rửa mặt", "sữa rửa", "srm", "rửa mặt"],
    "toner": ["toner"],
    "serum": ["serum"],
    "kem_duong": ["kem dưỡng", "kem dưỡng ẩm"],
    "combo": ["combo", "bộ skincare", "full bộ", "trọn bộ", "set skincare"],
    "kem_duong_mat": ["kem dưỡng mắt", "kem mắt", "dưỡng mắt"],
    "sap_duong_dem": ["sáp dưỡng đêm", "sáp dưỡng", "sáp đêm"],
    "bha": ["bha", "tẩy tế bào chết", "tẩy da chết"],
    "vitamin_c": ["vitamin c", "vitaminc"],
    "bo_8_san_pham": ["bộ 8 sản phẩm", "bộ 8 món", "full bộ 8", "8 sản phẩm", "8 món"]
}

PRODUCT_INTENT = {
    "sua_rua_mat": "iSuaruamat",
    "toner": "iToner",
    "serum": "iSerum",
    "kem_duong": "iKemduong",
    "combo": "iCombo",
    "kem_duong_mat": "iKemduongmat",
    "sap_duong_dem": "iSapduongdem",
    "bha": "iTaytebaochet",
    "vitamin_c": "iVitaminC",
    "bo_8_san_pham": "i8sanpham"
}

SKIN_TYPE_KEYWORDS = {
    "da_kho": ["da khô", "da mình khô", "mình da khô"],
    "da_dau": ["da dầu", "da nhờn", "da mình dầu"],
    "da_hon_hop": ["da hỗn hợp"],
    "da_nhay_cam": ["da nhạy cảm"],
    "da_mun": ["da mụn", "da dễ nổi mụn", "dễ nổi mụn"],
    "da_thuong": ["da thường"]
}

QUESTION_KEYWORDS = {
    "ship": ["giá ship", "phí ship", "ship", "freeship", "vận chuyển", "giao hàng", "khu vực giao"],
    "thanh_toan": ["thanh toán", "chuyển khoản", "mã qr", "tiền mặt", "momo", "zalopay", "cod"],
    "doi_tra": ["đổi trả", "trả hàng", "hoàn trả", "hoàn tiền"],
    "huy_don": ["hủy đơn", "huỷ đơn", "đổi ý không mua", "không mua nữa"],
    "dat_hang": ["đặt hàng", "chốt đơn", "lên đơn", "đặt", "lấy sản phẩm"],
    "con_hang": ["còn hàng", "còn không", "còn sản phẩm", "hết hàng"],
    "han_su_dung": ["hạn sử dụng", "hết hạn", "còn hạn bao lâu", "sau khi mở nắp", "pao"],
    "giam_gia": ["giảm giá", "ưu đãi", "khuyến mãi", "chương trình giảm"],
    "bao_quan": ["bảo quản", "để ở đâu", "tủ lạnh", "tránh nắng"],
    "khieu_nai": ["khiếu nại", "nhân viên", "thái độ", "dịch vụ chưa tốt"],
    "hieu_qua": ["hiệu quả", "bao lâu thì", "khi nào đẹp da", "thấy tác dụng"],
    "gia": ["giá bao nhiêu", "bao nhiêu tiền", "giá", "nhiêu tiền"],
    "dung_tich": ["dung tích", "bao nhiêu ml", "bao nhiêu g", "size"],
    "cach_dung": ["cách dùng", "dùng như nào", "dùng thế nào", "sử dụng như thế nào", "dùng sao"],
    "thoi_diem": ["dùng lúc nào", "khi nào dùng", "dùng buổi sáng", "dùng buổi tối"],
    "thanh_phan": ["thành phần", "chứa gì", "có những chất gì"],
    "cong_dung": ["công dụng", "tác dụng", "giúp gì"],
    "phu_hop": ["phù hợp", "có hợp không", "dùng được không", "da nhạy cảm dùng", "da khô dùng"]
}

SERVICE_INTENT = {
    "ship": "iShip",
    "thanh_toan": "iThanhtoan",
    "doi_tra": "iHoantrahang",
    "huy_don": "iHuydon",
    "dat_hang": "iDathang",
    "con_hang": "iConhang",
    "han_su_dung": "iHansudung",
    "giam_gia": "iGiamgia",
    "bao_quan": "iBaoquan",
    "khieu_nai": "iKhieunai",
    "hieu_qua": "iHieuqua"
}


def detect_product(text):
    text_normalized = normalize(text)
    matches = []
    for product, keywords in PRODUCT_KEYWORDS.items():
        for keyword in keywords:
            keyword_normalized = normalize(keyword)
            if keyword_normalized and keyword_normalized in text_normalized:
                matches.append((len(keyword_normalized), product))
    if matches:
        matches.sort(reverse=True)
        return matches[0][1]
    return None


def detect_skin_type(text):
    text_normalized = normalize(text)
    for skin_type, keywords in SKIN_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if normalize(keyword) in text_normalized:
                return skin_type
    return None


def detect_question_type(text):
    text_normalized = normalize(text)
    priority_order = [
        "ship", "thanh_toan", "doi_tra", "huy_don", "dat_hang",
        "con_hang", "han_su_dung", "giam_gia", "bao_quan", "khieu_nai",
        "hieu_qua", "thanh_phan", "cach_dung", "thoi_diem", "dung_tich",
        "cong_dung", "phu_hop", "gia"
    ]
    for question_type in priority_order:
        keywords = QUESTION_KEYWORDS.get(question_type, [])
        for keyword in keywords:
            if normalize(keyword) in text_normalized:
                return question_type
    return None


def similarity(text1, text2):
    return SequenceMatcher(None, normalize(text1), normalize(text2)).ratio()


def find_intent_by_name(intent_name):
    if intent_name in intent_data:
        return intent_name
    return None


def detect_intent(user_text, current_product=None):
    text = normalize(user_text)
    product = detect_product(text)
    skin_type = detect_skin_type(text)
    question_type = detect_question_type(text)

    if product is None:
        product = current_product

    if question_type in SERVICE_INTENT:
        service_intent = find_intent_by_name(SERVICE_INTENT[question_type])
        if service_intent:
            return service_intent, product, skin_type, question_type, 100

    if skin_type is not None:
        if "iLoaida" in intent_data:
            return "iLoaida", product, skin_type, question_type, 100

    if product in PRODUCT_INTENT:
        product_intent = find_intent_by_name(PRODUCT_INTENT[product])
        if product_intent:
            return product_intent, product, skin_type, question_type, 90

    best_intent = None
    best_score = 0
    search_text = text
    if product:
        search_text += " " + normalize(product.replace("_", " "))

    for intent, data in intent_data.items():
        score = 0
        for keyword in data["keywords"]:
            keyword = normalize(keyword)
            if keyword and keyword in search_text:
                score += 4 + len(keyword.split())

        for training in data["training"]:
            sim = similarity(search_text, training)
            if sim >= 0.80:
                score += 8
            elif sim >= 0.65:
                score += 5
            elif sim >= 0.50:
                score += 2

        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < 2:
        return None, product, skin_type, question_type, best_score

    return best_intent, product, skin_type, question_type, best_score


# ============================================================
# 5. XỬ LÝ PHẢN HỒI (RESPONSE)
# ============================================================

def split_sentences(text):
    text = cell_to_text(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip() for part in parts if part.strip()]


def choose_product_response(responses, question_type):
    full_text = "\n".join(responses)
    sentences = split_sentences(full_text)

    if question_type == "gia":
        for sentence in sentences:
            s = normalize(sentence)
            if re.search(r"\d", s) and ("gia" in s or "dong" in s or "k" in s):
                return sentence
    elif question_type == "dung_tich":
        for sentence in sentences:
            s = normalize(sentence)
            if re.search(r"\d+\s*(ml|g)\b", s):
                return sentence
    elif question_type in ["cach_dung", "thoi_diem"]:
        for sentence in sentences:
            s = normalize(sentence)
            if "dung" in s or "sau buoc" in s or "buoi sang" in s or "buoi toi" in s or "lan/ngay" in s:
                return sentence
    elif question_type == "thanh_phan":
        for sentence in sentences:
            if "thanh phan" in normalize(sentence):
                return sentence
    elif question_type == "cong_dung":
        for sentence in sentences:
            s = normalize(sentence)
            if "cong dung" in s or "tac dung" in s:
                return sentence
    elif question_type == "phu_hop":
        for sentence in sentences:
            s = normalize(sentence)
            if "phu hop" in s or "da nhay cam" in s or "da kho" in s or "da dau" in s or "da mun" in s:
                return sentence

    return full_text


def choose_response(intent, question_type, skin_type=None):
    if intent not in intent_data:
        return None

    responses = intent_data[intent]["responses"]
    if not responses:
        return None

    if intent == "iLoaida":
        if skin_type in ["da_kho", "da_mun", "da_dau"]:
            for response in responses:
                r = normalize(response)
                if "da kho" in r and "da mun" in r and "da dau" in r:
                    return response
        if skin_type in ["da_hon_hop", "da_thuong", "da_nhay_cam"]:
            for response in responses:
                r = normalize(response)
                if "da hon hop" in r and "da thuong" in r and "da nhay cam" in r:
                    return response
        return "\n".join(responses)

    if intent in ["iChaohoi", "iLoichaotambiet"]:
        return random.choice(responses)

    if intent == "iConhang":
        return "\n".join(responses)

    service_intents = [
        "iShip", "iThanhtoan", "iHoantrahang", "iDathang", "iGiamgia",
        "iHieuqua", "iHuydon", "iBaoquan", "iKhieunai", "iHansudung",
        "iCachdungcombo", "i8sanpham", "iCombo"
    ]

    if intent in service_intents:
        return "\n".join(responses)

    return choose_product_response(responses, question_type)


# ============================================================
# 6. CHƯƠNG TRÌNH CHATBOT CHẠY TRÊN TERMINAL
# ============================================================

current_product = None
current_skin_type = None


def chatbot_reply(user_text):
    global current_product
    global current_skin_type

    if not user_text.strip():
        return "Dạ bạn hãy nhập câu hỏi để mình hỗ trợ nhé!"

    intent, product, skin_type, question_type, score = detect_intent(
        user_text, current_product
    )

    if product is not None:
        current_product = product

    if skin_type is not None:
        current_skin_type = skin_type

    if intent is None:
        return (
            "Dạ mình chưa hiểu rõ câu hỏi của bạn ạ. "
            "Bạn có thể hỏi về sản phẩm, giá, cách dùng, "
            "thành phần, công dụng, phí ship, đặt hàng, "
            "thanh toán hoặc đổi trả nhé!"
        )

    if skin_type is None:
        skin_type = current_skin_type

    answer = choose_response(intent, question_type, skin_type)

    if not answer:
        return "Dạ hiện tại mình chưa có câu trả lời cho nội dung này trong kịch bản ạ."

    return answer


@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat_api():
    payload = request.get_json(silent=True) or {}
    reply = chatbot_reply(payload.get('message', ''))
    return jsonify({'response': reply, 'reply': reply})


@app.get('/api/health')
def health_check():
    return jsonify({'status': 'ok'})


def run_terminal_chatbot():
    print("\n" + "=" * 60)
    print(" CHATBOT CHĂM SÓC KHÁCH HÀNG SUGAR RUSH (VS CODE)")
    print("=" * 60)
    print("Nhập câu hỏi để bắt đầu trò chuyện.")
    print("Gõ 'thoat', 'exit' hoặc 'quit' để kết thúc.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nKhách hàng: ")
            if normalize(user_input) in ["thoat", "exit", "quit"]:
                print("\nSugar Rush: Cảm ơn bạn đã quan tâm và ủng hộ Sugar Rush. Chúc bạn một ngày tốt lành ạ!")
                break

            answer = chatbot_reply(user_input)
            print("\nSugar Rush:", answer)
        except KeyboardInterrupt:
            print("\nSugar Rush: Tạm biệt bạn!")
            break


if __name__ == "__main__":
    if os.environ.get('CHATBOT_MODE') == 'terminal':
        run_terminal_chatbot()
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)