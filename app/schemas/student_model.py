import pandas as pd
import pickle
import os
from pyBKT.models import Model
from typing import Dict

# Đường dẫn lưu các mô hình BKT của học sinh [cite: 94]
STUDENT_MODELS_DIR = "app/data/student_models/"
os.makedirs(STUDENT_MODELS_DIR, exist_ok=True)

# Các tham số tiên nghiệm do chuyên gia xác định [cite: 113, 117]
BKT_PRIORS = {
    'prior': 0.3,    # P(L0)
    'learns': 0.15,  # P(T)
    'guesses': 0.2,  # P(G)
    'slips': 0.1     # P(S)
}

class StudentBKTManager:
    def __init__(self, student_id: str, all_kcs: list):
        self.student_id = student_id
        self.model_path = os.path.join(STUDENT_MODELS_DIR, f"{student_id}_bkt.pkl")
        self.interactions_path = os.path.join(STUDENT_MODELS_DIR, f"{student_id}_interactions.csv")
        self.all_kcs = all_kcs
        self.model = self._load_model()
        self.interactions_df = self._load_interactions()

    def _load_model(self) -> Model:
        """Tải mô hình BKT đã lưu hoặc tạo mới nếu chưa tồn tại[cite: 128]."""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # Khởi tạo mô hình mới với các tham số tiên nghiệm [cite: 114, 117]
            model = Model(seed=42, num_fits=1)
            # Không huấn luyện ban đầu, chỉ thiết lập tham số
            return model

    def _load_interactions(self) -> pd.DataFrame:
        """Tải lịch sử tương tác của học sinh."""
        if os.path.exists(self.interactions_path):
            return pd.read_csv(self.interactions_path)
        else:
            # Tạo DataFrame trống với các cột cần thiết cho pyBKT [cite: 106, 110]
            return pd.DataFrame(columns=['order_id', 'user_id', 'skill_name', 'correct'])

    def _save_model(self):
        """Lưu đối tượng mô hình BKT của học sinh[cite: 128]."""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def _save_interactions(self):
        """Lưu lịch sử tương tác vào file CSV."""
        self.interactions_df.to_csv(self.interactions_path, index=False)

    def update_with_answer(self, kc: str, is_correct: bool):
        """Thêm một tương tác mới và huấn luyện lại (cập nhật) mô hình BKT."""
        new_order_id = (self.interactions_df['order_id'].max() + 1) if not self.interactions_df.empty else 1
        
        new_interaction = pd.DataFrame([{
            'order_id': new_order_id,
            'user_id': self.student_id,
            'skill_name': kc,
            'correct': int(is_correct) # pyBKT yêu cầu giá trị 0 hoặc 1 [cite: 111]
        }])
        
        self.interactions_df = pd.concat([self.interactions_df, new_interaction], ignore_index=True)
        
        # Huấn luyện lại mô hình trên toàn bộ lịch sử tương tác [cite: 118, 126]
        # Đối với BKT, đây là cách cập nhật trạng thái
        self.model.fit(data=self.interactions_df, priors=BKT_PRIORS)
        
        self._save_model()
        self._save_interactions()

    def get_mastery_vector(self) -> Dict[str, float]:
        """
        Lấy vector xác suất thành thạo hiện tại của học sinh cho tất cả các KC[cite: 121].
        """
        mastery_prob_vector = {}
        
        if self.interactions_df.empty:
            # Nếu chưa có tương tác, tất cả KC đều ở xác suất tiên nghiệm P(L0)
            for kc in self.all_kcs:
                mastery_prob_vector[kc] = BKT_PRIORS['prior']
            return mastery_prob_vector

        # Dự đoán trạng thái kiến thức sau các tương tác [cite: 123]
        preds = self.model.predict(data=self.interactions_df)
        
        for kc in self.all_kcs:
            kc_preds = preds[preds['skill_name'] == kc]
            if not kc_preds.empty:
                # Lấy xác suất thành thạo mới nhất cho KC đã làm [cite: 123]
                last_mastery_prob = kc_preds['state_predictions'].iloc[-1]
                mastery_prob_vector[kc] = last_mastery_prob
            else:
                # Nếu chưa làm KC này, sử dụng xác suất tiên nghiệm P(L0) [cite: 124]
                mastery_prob_vector[kc] = BKT_PRIORS['prior']
                
        return mastery_prob_vector