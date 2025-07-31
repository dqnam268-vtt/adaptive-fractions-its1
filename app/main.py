# adaptive-fractions-its1/app/main.py

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import các router và các lớp logic từ các gói con trong cùng gói 'app'
from .api.router import router
from .core.adaptation import AdaptationEngine
from .core.student_bkt_manager import StudentBKTManager

# BỎ CÁC IMPORT LIÊN QUAN ĐẾN CƠ SỞ DỮ LIỆU SQL NÀY
# from .database import engine, Base
# from .models import Student, Interaction

app = FastAPI(
    title="Hệ Thống Luyện Tập Phân Số Thích Ứng",
    description="Ứng dụng giúp học sinh luyện tập phân số với khả năng thích ứng dựa trên trình độ.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "null",
        "https://your_username.github.io",   # THAY THẾ BẰNG URL GITHUB PAGES CỦA BẠN (VD: https://dqnam268-vtt.github.io)
        "https://your_username.github.io/your_repository_name", # Hoặc đường dẫn cụ thể nếu repo name nằm trong URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Ứng dụng đang khởi động...")

    # BỎ CÁC DÒNG TẠO BẢNG CƠ SỞ DỮ LIỆU SQL NÀY
    # Base.metadata.create_all(bind=engine)
    # print("Đã tạo hoặc kiểm tra các bảng cơ sở dữ liệu.")

    # Đường dẫn đến question_bank.json
    question_bank_path = 'app/data/question_bank.json'

    try:
        with open(question_bank_path, "r", encoding="utf-8") as f:
            question_data = json.load(f)
        app.state.question_bank = question_data
        print(f"Đã tải {len(question_data)} câu hỏi từ {question_bank_path}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp '{question_bank_path}'. Vui lòng đảm bảo tệp nằm đúng đường dẫn.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể đọc tệp '{question_bank_path}'. Đảm bảo tệp là JSON hợp lệ.")
        exit(1)

    all_kcs = sorted(list(set(q["knowledge_component"] for q in question_data)))
    app.state.all_knowledge_components = all_kcs
    print(f"Đã phát hiện {len(all_kcs)} thành phần kiến thức (Knowledge Components): {', '.join(all_kcs)}")

    app.state.adaptation_engine = AdaptationEngine(all_kcs=all_kcs)
    print("Đã khởi tạo Adaptation Engine.")

    # student_managers sẽ vẫn là một dictionary trong bộ nhớ tạm thời
    # để quản lý các phiên làm việc của học sinh đang hoạt động.
    # Dữ liệu thực tế sẽ được đọc/ghi vào DB thông qua StudentBKTManager.
    app.state.student_managers = {}
    print("Đã khởi tạo bộ quản lý học sinh (cache).")
    print("Ứng dụng khởi động hoàn tất.")

app.include_router(router, prefix="/api/v1")