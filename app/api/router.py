from fastapi import APIRouter, HTTPException, Query
from typing import List
import random

from app.schemas.question import QuestionPublic
from app.schemas.student import AnswerSubmission, SubmissionResult, DashboardData
from app.core.student_model import StudentBKTManager
from app.core.adaptation import AdaptationEngine

# Khởi tạo router
router = APIRouter()

# Tải các tài nguyên một lần khi ứng dụng khởi động (sẽ được quản lý bởi main.py)
# Đây là các biến toàn cục cho router này
question_bank: List[dict] = []
all_kcs: List[str] = []
adaptation_engine: AdaptationEngine = None

# Định nghĩa các endpoint dựa trên Bảng 3 [cite: 176]

@router.get("/session/next-question", response_model=QuestionPublic)
def get_next_question(student_id: str = Query(...)):
    """
    Lấy câu hỏi tiếp theo cho một học sinh dựa trên trạng thái hiện tại của em đó[cite: 177].
    """
    if not student_id:
        raise HTTPException(status_code=400, detail="Cần có student_id")

    student_manager = StudentBKTManager(student_id=student_id, all_kcs=all_kcs)
    
    # Sử dụng cơ chế thích ứng để chọn KC và độ khó
    next_kc, next_difficulty = adaptation_engine.get_next_question_spec(student_manager)

    # Tìm một câu hỏi phù hợp trong ngân hàng câu hỏi
    candidate_questions = [
        q for q in question_bank 
        if q['knowledge_component'] == next_kc and q['difficulty_level'] == next_difficulty
    ]

    if not candidate_questions:
        # Fallback: nếu không tìm thấy câu hỏi chính xác, nới lỏng điều kiện
        candidate_questions = [q for q in question_bank if q['knowledge_component'] == next_kc]
        if not candidate_questions:
            # Fallback cuối cùng: chọn một câu hỏi ngẫu nhiên
            candidate_questions = question_bank

    chosen_question = random.choice(candidate_questions)
    
    # Trả về đối tượng public, không có đáp án [cite: 177]
    return QuestionPublic(**chosen_question)


@router.post("/session/submit-answer", response_model=SubmissionResult)
def submit_answer(submission: AnswerSubmission):
    """
    Gửi câu trả lời của học sinh, cập nhật mô hình người học, và trả về kết quả[cite: 177].
    """
    # Tìm câu hỏi trong ngân hàng
    question = next((q for q in question_bank if q['question_id'] == submission.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi") # [cite: 190]

    # Kiểm tra câu trả lời
    is_correct = (submission.submitted_answer == question['correct_answer'])
    
    # Cập nhật mô hình BKT của học sinh
    student_manager = StudentBKTManager(student_id=submission.student_id, all_kcs=all_kcs)
    student_manager.update_with_answer(kc=question['knowledge_component'], is_correct=is_correct)

    feedback = "Chính xác! Làm tốt lắm!" if is_correct else f"Chưa đúng lắm. Đáp án đúng là {question['correct_answer']}."
    
    return SubmissionResult(
        is_correct=is_correct,
        correct_answer=question['correct_answer'],
        feedback=feedback
    )

@router.get("/students/{student_id}/dashboard", response_model=DashboardData)
def get_dashboard_data(student_id: str):
    """
    Lấy dữ liệu tổng quan về tiến độ của học sinh (vector xác suất thành thạo)[cite: 177].
    """
    student_manager = StudentBKTManager(student_id=student_id, all_kcs=all_kcs)
    mastery_vector = student_manager.get_mastery_vector()
    
    if not mastery_vector:
         raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu cho học sinh này") # [cite: 190]

    return DashboardData(
        student_id=student_id,
        mastery_prob_vector=mastery_vector
    )