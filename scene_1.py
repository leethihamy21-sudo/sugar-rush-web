import os
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Cấu hình đường dẫn thư mục chứa giao diện web đã build (thư mục dist)
app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)

# ==========================================
# 1. ĐỌC DỮ LIỆU TỪ FILE EXCEL
# ==========================================
file_name = "final_scene.xlsx"

if os.path.exists(file_name):
    file_path = file_name
else:
    file_path = file_name

print(f"Đang cố gắng đọc file từ: {file_path}")

try:
    xls = pd.ExcelFile(file_path)
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"✅ Đọc thành công sheet: '{sheet_name}' với {len(df)} dòng dữ liệu từ file Excel!")
except Exception as e:
    print(f"❌ Không tìm thấy file hoặc lỗi đọc file: {e}")
    df = pd.DataFrame()

# ==========================================
# 2. HÀM TÌM KIẾM CÂU TRẢ LỜI
# ==========================================
def find_response(user_text):
    if df.empty:
        return "Dạ hiện tại file Excel chưa được tải lên đúng cách."
    
    user_text = user_text.lower()
    best_match_idx = -1
    max_score = 0
    
    for idx, row in df.iterrows():
        training_data = str(row.get('Training', ''))
        entities_data = str(row.get('Entities', ''))
        
        keywords = (training_data + "\n" + entities_data).lower().split()
        score = sum(1 for word in keywords if word in user_text and len(word) > 2)
        
        if score > max_score:
            max_score = score
            best_match_idx = idx
            
    if best_match_idx != -1 and max_score > 0:
        return str(df.iloc[best_match_idx]['Responses'])
    else:
        return "Dạ hiện tại em chưa hiểu rõ ý bạn lắm. Bạn có thể hỏi cụ thể hơn về: giá, thành phần, công dụng, loại da, cách dùng hoặc đơn hàng nhé ạ!"

# ==========================================
# 3. API NHẬN TIN NHẮN CHATBOT
# ==========================================
@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '')
    reply = find_response(user_message)
    return jsonify({'reply': reply, 'response': reply})

@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})

# ==========================================
# 4. PHỤC VỤ GIAO DIỆN WEB (TRÁNH LỖI 404)
# ==========================================
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)