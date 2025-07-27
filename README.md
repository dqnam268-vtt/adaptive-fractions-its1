Hệ Thống Dạy Học Thông Minh Thích Ứng - Phân Số (Adaptive Fractions ITS) 🎓🧮
Một Hệ Thống Dạy Học Thông Minh (Intelligent Tutoring System - ITS) được xây dựng bằng Python và FastAPI, được thiết kế để cung cấp trải nghiệm học tập được cá nhân hóa cho chủ đề phân số. Hệ thống sẽ tự động điều chỉnh độ khó và loại câu hỏi dựa trên mô hình hóa kiến thức của từng học sinh.

✨ Tính Năng Cốt Lõi
Lựa chọn câu hỏi thích ứng: Sử dụng mô hình học máy (Decision Tree) để chọn câu hỏi tiếp theo phù hợp nhất với trình độ hiện tại của học sinh.

Mô hình hóa kiến thức học sinh (Student Modeling): Theo dõi và cập nhật liên tục trạng thái kiến thức của học sinh sau mỗi câu trả lời.

API dựa trên FastAPI: Cung cấp các endpoint RESTful để giao tiếp với hệ thống, dễ dàng tích hợp với các giao diện người dùng (frontend).

Ngân hàng câu hỏi linh hoạt: Quản lý câu hỏi thông qua một tệp JSON, giúp dễ dàng mở rộng và chỉnh sửa.

🛠️ Công Nghệ Sử Dụng
Backend: Python, FastAPI

Machine Learning: Scikit-learn

Server: Uvicorn

Data Handling: Pydantic

📂 Cấu Trúc Dự Án
adaptive-fractions-its/
|-- app/
|   |-- __init__.py
|   |-- api/
|   |   |-- __init__.py
|   |   |-- router.py         # Định nghĩa các API endpoints (ví dụ: lấy câu hỏi, nộp câu trả lời)
|   |-- core/
|   |   |-- __init__.py
|   |   |-- adaptation.py     # Logic cốt lõi cho việc lựa chọn câu hỏi thích ứng
|   |   |-- student_model.py  # Quản lý và cập nhật trạng thái kiến thức của học sinh
|   |-- data/
|   |   |-- question_bank.json # Ngân hàng câu hỏi về phân số
|   |   |-- student_models/    # (Tùy chọn) Nơi lưu trữ các mô hình học sinh
|   |   |-- dt_model.pkl       # Mô hình Decision Tree đã được huấn luyện
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- question.py       # Pydantic schema cho đối tượng Câu hỏi
|   |   |-- student.py        # Pydantic schema cho đối tượng Học sinh
|   |-- main.py               # Điểm khởi đầu của ứng dụng FastAPI
|-- requirements.txt          # Các thư viện Python cần thiết
|-- README.md                 # Tài liệu hướng dẫn dự án

🚀 Bắt Đầu Nhanh
Yêu cầu tiên quyết
Python 3.9+

Pip

Cài đặt và Chạy
Clone repository về máy:

git clone https://your-repository-url/adaptive-fractions-its.git
cd adaptive-fractions-its

Tạo và kích hoạt môi trường ảo (khuyến khích):

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

Cài đặt các thư viện cần thiết:

pip install -r requirements.txt

Chạy server FastAPI: Từ thư mục gốc adaptive-fractions-its/, chạy lệnh sau:

uvicorn app.main:app --reload

--reload sẽ tự động khởi động lại server mỗi khi có thay đổi trong code.

Truy cập tài liệu API: Mở trình duyệt và truy cập vào địa chỉ http://127.0.0.1:8000/docs. Bạn sẽ thấy giao diện Swagger UI, nơi bạn có thể xem và tương tác trực tiếp với các API endpoints.

🤖 API Endpoints
Hệ thống cung cấp các API endpoint chính sau (chi tiết có tại /docs):

Method

Endpoint

Mô tả

POST

/api/students/

Tạo một hồ sơ mới cho học sinh.

GET

/api/questions/next/{student_id}

Lấy câu hỏi thích ứng tiếp theo cho một học sinh.

POST

/api/answers/

Gửi câu trả lời của học sinh và cập nhật mô hình.

GET

/api/students/{student_id}/progress

Lấy thông tin về tiến trình học tập của học sinh.

🤝 Đóng Góp
Chúng tôi luôn chào đón các đóng góp! Vui lòng fork repository, tạo một nhánh mới cho tính năng của bạn, và gửi một Pull Request.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 Giấy Phép
Dự án này được cấp phép theo Giấy phép MIT. Xem tệp LICENSE để biết thêm chi tiết.