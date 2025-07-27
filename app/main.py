from fastapi import FastAPI
import json

from app.api import router as api_router
from app.core.adaptation import AdaptationEngine

# Tạo ứng dụng FastAPI [cite: 79]
app = FastAPI(
    title="Adaptive Fractions ITS API",
    description="API cho Hệ thống Luyện tập Thích ứng về Phân số",
    version="1.0.0"
)

@app.on_event("startup")
def load_resources():
    """
    Nạp các tài nguyên cần thiết vào bộ nhớ khi ứng dụng khởi động[cite: 69].
    """
    # 1. Tải ngân hàng câu hỏi
    with open("app/data/question_bank.json", "r", encoding="utf-8") as f:
        api_router.question_bank = json.load(f)
    print(f"Đã tải {len(api_router.question_bank)} câu hỏi vào bộ nhớ.")

    # 2. Lấy danh sách tất cả các Thành phần Kiến thức (KC) từ ngân hàng câu hỏi [cite: 23]
    all_kcs = sorted(list(set(q['knowledge_component'] for q in api_router.question_bank)))
    api_router.all_kcs = all_kcs
    print(f"Tìm thấy {len(all_kcs)} thành phần kiến thức.")

    # 3. Khởi tạo Cơ chế Thích ứng
    api_router.adaptation_engine = AdaptationEngine(all_kcs=all_kcs)
    print("Cơ chế Thích ứng đã được khởi tạo.")


# Liên kết router API với ứng dụng chính
app.include_router(api_router.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Chào mừng bạn đến với API của Hệ thống Luyện tập Thích ứng!"}