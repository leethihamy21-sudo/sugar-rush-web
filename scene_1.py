import os
import unicodedata

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
WORKBOOK_PATH = os.path.join(BASE_DIR, 'Kịch_bản_hc_updated.xlsx')

try:
    workbook = pd.ExcelFile(WORKBOOK_PATH)
    data = pd.read_excel(WORKBOOK_PATH, sheet_name=workbook.sheet_names[0])
    print(f"Đọc thành công workbook updated với {len(data)} dòng dữ liệu.")
except Exception as error:
    print(f"Lỗi đọc workbook: {error}")
    data = pd.DataFrame()


def remove_accents(text):
    normalized = unicodedata.normalize('NFD', str(text))
    without_marks = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_marks.replace('đ', 'd').replace('Đ', 'D').lower().strip()


def _training_phrases(value):
    return [remove_accents(phrase) for phrase in str(value).split(',') if phrase.strip()]


def _response_text(value):
    """Keep line breaks from Excel consistent in the API response."""
    return str(value).replace('\r\n', '\n').replace('\r', '\n')


# ==========================================
# HÀM TÌM KIẾM: ƯU TIÊN CỤM TỪ KHỚP CỤ THỂ NHẤT
# ==========================================
def find_response(user_text):
    if data.empty:
        return "Dạ hiện tại file Excel chưa được tải lên đúng cách."

    clean_user_text = remove_accents(user_text)
    best_match_idx = -1
    best_score = -1

    for idx, row in data.iterrows():
        for phrase in _training_phrases(row.get('Training', '')):
            if phrase == clean_user_text:
                score = 10000 + len(phrase)
            elif phrase in clean_user_text:
                score = 5000 + len(phrase)
            elif clean_user_text in phrase:
                # Short product names should match their dedicated product row,
                # but never outrank a longer, intent-specific phrase.
                score = len(clean_user_text) if len(phrase) > len(clean_user_text) else 1000 + len(phrase)
            else:
                continue

            if score > best_score:
                best_score = score
                best_match_idx = idx

    if best_match_idx >= 0:
        return _response_text(data.iloc[best_match_idx]['Responses'])
    return "Dạ hiện tại em chưa hiểu rõ ý bạn lắm. Bạn có thể hỏi cụ thể hơn về giá, thành phần hoặc công dụng nhé ạ!"


@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json(silent=True) or {}
    reply = find_response(payload.get('message', ''))
    return jsonify({'response': reply, 'reply': reply})


@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.get('/')
def index():
    return send_from_directory(DIST_DIR, 'index.html')


@app.get('/<path:requested_path>')
def website_files(requested_path):
    requested_file = os.path.join(DIST_DIR, requested_path)
    if os.path.isfile(requested_file):
        return send_from_directory(DIST_DIR, requested_path)
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)