import pandas as pd
import pickle
import os
import random
from typing import Tuple, Dict

# Giả định mô hình đã được huấn luyện và lưu [cite: 95]
DT_MODEL_PATH = "app/data/dt_model.pkl"

class AdaptationEngine:
    def __init__(self, all_kcs: list):
        self.all_kcs = all_kcs
        self.dt_model = self._load_decision_tree()

    def _load_decision_tree(self):
        """Tải Cây quyết định đã được huấn luyện."""
        # Trong một ứng dụng thực tế, cần có một quy trình huấn luyện và lưu mô hình này.
        # Ở đây, chúng ta giả định nó tồn tại hoặc trả về None nếu không có.
        if os.path.exists(DT_MODEL_PATH):
            with open(DT_MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        else:
            print("Cảnh báo: Không tìm thấy tệp dt_model.pkl. Hệ thống sẽ chạy ở chế độ heuristic.")
            return None

    def _get_heuristic_choice(self, mastery_vector: Dict[str, float]) -> Tuple[str, int]:
        """
        Logic heuristic đơn giản cho vấn đề 'khởi đầu lạnh' hoặc khi không có Cây quyết định[cite: 144].
        """
        # Tìm các KC có xác suất thành thạo thấp nhất
        min_mastery = min(mastery_vector.values())
        low_mastery_kcs = [kc for kc, prob in mastery_vector.items() if prob == min_mastery]
        
        # Chọn ngẫu nhiên một KC từ danh sách yếu nhất
        chosen_kc = random.choice(low_mastery_kcs)
        
        # Chiến lược chọn độ khó dựa trên xác suất thành thạo [cite: 147, 148]
        if min_mastery < 0.5:
            difficulty = random.choice([1, 2]) # Câu hỏi dễ
        elif 0.5 <= min_mastery < 0.9:
            difficulty = random.choice([3, 4]) # Câu hỏi trung bình
        else:
            difficulty = 5 # Câu hỏi khó
            
        return chosen_kc, difficulty

    def _create_feature_vector(self, student_manager) -> pd.DataFrame:
        """
        Xây dựng vector đặc trưng cho Cây quyết định như trong tài liệu[cite: 133].
        """
        features = {}
        
        # Đặc trưng 1: Vector xác suất thành thạo [cite: 134]
        mastery_vector = student_manager.get_mastery_vector()
        features.update(mastery_vector)
        
        interactions = student_manager.interactions_df
        if interactions.empty:
            # Giá trị mặc định nếu chưa có tương tác
            features['recent_accuracy'] = 0.0
            features['last_kc_attempted'] = 'none'
            features['last_difficulty_attempted'] = 0
            # ... các đặc trưng khác
            return pd.DataFrame([features], columns=self.dt_model.feature_names_in_)

        # Đặc trưng 2: Độ chính xác gần đây [cite: 135]
        last_3 = interactions.tail(3)
        features['recent_accuracy'] = last_3['correct'].mean()

        # Đặc trưng 3 & 4: KC và độ khó lần cuối [cite: 137]
        last_interaction = interactions.iloc[-1]
        features['last_kc_attempted'] = last_interaction['skill_name']
        # Giả sử chúng ta lưu `difficulty_level` trong tệp tương tác
        # features['last_difficulty_attempted'] = last_interaction['difficulty_level']
        
        # Các đặc trưng khác như time_on_last_q, error_streak_on_kc sẽ cần thêm cột trong
        # tệp interactions.csv để tính toán [cite: 136, 138]
        
        # Cần chuyển đổi các đặc trưng phân loại (categorical) thành số
        # Ví dụ: pd.get_dummies
        # Mã này cần được mở rộng để khớp với lúc huấn luyện Cây quyết định.
        
        # Tạm thời trả về một dict để minh họa
        return features

    def get_next_question_spec(self, student_manager) -> Tuple[str, int]:
        """
        Quyết định KC và độ khó cho câu hỏi tiếp theo.
        """
        if not self.dt_model:
            # Nếu không có mô hình, sử dụng chiến lược heuristic [cite: 143]
            mastery_vector = student_manager.get_mastery_vector()
            return self._get_heuristic_choice(mastery_vector)
        
        # 1. Kỹ thuật đặc trưng [cite: 133]
        feature_vector = self._create_feature_vector(student_manager)
        
        # 2. Dự đoán bằng Cây quyết định
        # Đầu ra dự kiến là một chuỗi dạng "kc_difficulty" [cite: 156]
        prediction = self.dt_model.predict(feature_vector)[0]
        
        # 3. Tách chuỗi để lấy KC và độ khó
        parts = prediction.rsplit('_', 1)
        next_kc = parts[0]
        next_difficulty = int(parts[1])
        
        return next_kc, next_difficulty