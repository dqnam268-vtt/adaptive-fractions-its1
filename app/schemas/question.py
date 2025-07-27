from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Cấu trúc của một gợi ý
class Hint(BaseModel):
    hint_id: str
    text: str

# Cấu trúc nội dung câu hỏi
class Content(BaseModel):
    text: str
    image: Optional[str] = None
    formula_latex: Optional[str] = None

# Mô hình đầy đủ của một câu hỏi (sử dụng nội bộ)
class QuestionInternal(BaseModel):
    question_id: str
    content: Content
    question_type: str
    options: List[str]
    correct_answer: str
    knowledge_component: str
    difficulty_level: int
    misconception_target: List[str]
    hints: List[Hint]

# Mô hình câu hỏi gửi đến frontend (loại bỏ đáp án)
# Schema cho Phản hồi của GET /session/next-question [cite: 177, 184]
class QuestionPublic(BaseModel):
    question_id: str
    content: Content
    question_type: str
    options: List[str]
    knowledge_component: str
    difficulty_level: int