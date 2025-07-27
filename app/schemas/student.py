from pydantic import BaseModel
from typing import Dict

# Schema cho Body Yêu cầu của POST /session/submit-answer [cite: 177, 181]
class AnswerSubmission(BaseModel):
    student_id: str
    question_id: str
    submitted_answer: str
    time_on_task_seconds: int

# Schema cho Phản hồi Thành công của POST /session/submit-answer [cite: 177]
class SubmissionResult(BaseModel):
    is_correct: bool
    correct_answer: str
    feedback: str # Ví dụ: "Chính xác!" hoặc "Chưa đúng lắm."

# Schema cho Phản hồi Thành công của GET /students/{student_id}/dashboard [cite: 177]
class DashboardData(BaseModel):
    student_id: str
    mastery_prob_vector: Dict[str, float]