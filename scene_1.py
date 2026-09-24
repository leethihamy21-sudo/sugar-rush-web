import os
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Cho phép web gọi vào API này
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN FILE EXCEL
# ==========================================
folder_name = os.path.join(BASE_DIR, "web")
file_name = "Kịch bản hc.xlsx"

if os.path.exists(os.path.join(BASE_DIR, file_name)):
    file_path = os.path.join(BASE_DIR, file_name)
elif os.path.exists(os.path.join(folder_name, file_name)):
    file_path = os.path.join(folder_name, file_name)
else:
    file_path = f"{folder_name}/{file_name}"

print(f"Đang cố gắng đọc file từ: {file_path}")

# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ FILE EXCEL
# ==========================================
try:
    xls = pd.ExcelFile(file_path)
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"✅ Đọc thành công sheet: '{sheet_name}' với {len(df)} dòng dữ liệu từ file Excel!")
except Exception as e:
    print(f"❌ Không tìm thấy file hoặc lỗi đọc file: {e}")
    df = pd.DataFrame()

# ==========================================
# 3. HÀM TÌM KIẾM CÂU TRẢ LỜI
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
# 4. TẠO API CHO WEB GỌI VÀO
# ==========================================
@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    reply = find_response(user_message)
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