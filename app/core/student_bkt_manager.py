# adaptive-fractions-its1/app/core/student_bkt_manager.py

import pandas as pd
import datetime
import json
import os # Import os để xử lý đường dẫn file

# Thư mục để lưu trữ dữ liệu học sinh.
# Trên Render, /opt/render/project/src/ là thư mục gốc của repo.
# Chúng ta sẽ tạo một thư mục 'student_data' tại đó.
DATA_DIR = "./student_data"

class StudentBKTManager:
    def __init__(self, student_id: str, all_kcs: list):
        self.student_id = student_id
        self.all_kcs = all_kcs
        self.p_L0 = 0.1
        self.p_T = 0.2
        self.p_S = 0.1
        self.p_G = 0.2

        self._ensure_data_dir_exists() # Đảm bảo thư mục lưu trữ tồn tại

        # Tên file cho mastery_vector của học sinh này
        self.mastery_file = os.path.join(DATA_DIR, f"{self.student_id}_mastery.json")
        # Tên file cho lịch sử tương tác của học sinh này
        self.interactions_file = os.path.join(DATA_DIR, f"{self.student_id}_interactions.csv")

        # Khởi tạo hoặc tải mastery_vector từ file JSON
        self.mastery_vector = self._load_mastery_from_file()
        if not self.mastery_vector: # Nếu chưa có file hoặc file rỗng, khởi tạo mới
            self.mastery_vector = {kc: self.p_L0 for kc in all_kcs}
            self._save_mastery_to_file() # Lưu trạng thái ban đầu vào file

        # Tải lịch sử tương tác hiện có hoặc tạo DataFrame rỗng
        self.interactions_df = self._load_interactions_from_file()

    def _ensure_data_dir_exists(self):
        """Đảm bảo thư mục lưu trữ dữ liệu tồn tại."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _load_mastery_from_file(self) -> dict:
        """Tải mastery_vector từ file JSON."""
        if os.path.exists(self.mastery_file):
            try:
                with open(self.mastery_file, 'r', encoding='utf-8') as f:
                    loaded_mastery = json.load(f)
                    # Đảm bảo các KC mới được thêm vào mastery_vector nếu chúng chưa có
                    for kc in self.all_kcs:
                        if kc not in loaded_mastery:
                            loaded_mastery[kc] = self.p_L0
                    return loaded_mastery
            except json.JSONDecodeError:
                print(f"Lỗi đọc file JSON {self.mastery_file}. Tạo mới.")
                return {} # Trả về rỗng nếu file JSON bị lỗi
        return {}

    def _save_mastery_to_file(self):
        """Lưu mastery_vector hiện tại vào file JSON."""
        with open(self.mastery_file, 'w', encoding='utf-8') as f:
            json.dump(self.mastery_vector, f, indent=4)

    def _load_interactions_from_file(self) -> pd.DataFrame:
        """Tải lịch sử tương tác từ file CSV."""
        if os.path.exists(self.interactions_file):
            try:
                return pd.read_csv(self.interactions_file)
            except pd.errors.EmptyDataError:
                print(f"File CSV {self.interactions_file} rỗng. Tạo DataFrame mới.")
                # Trả về DataFrame rỗng với các cột cần thiết
                return pd.DataFrame(columns=['timestamp', 'kc', 'is_correct', 'p_L_before', 'p_L_after'])
            except Exception as e:
                print(f"Lỗi đọc file CSV {self.interactions_file}: {e}. Tạo DataFrame mới.")
                return pd.DataFrame(columns=['timestamp', 'kc', 'is_correct', 'p_L_before', 'p_L_after'])
        return pd.DataFrame(columns=['timestamp', 'kc', 'is_correct', 'p_L_before', 'p_L_after'])

    def _save_interactions_to_file(self):
        """Lưu lịch sử tương tác vào file CSV."""
        self.interactions_df.to_csv(self.interactions_file, index=False)

    def update_mastery(self, kc: str, is_correct: bool):
        """
        Cập nhật xác suất thành thạo của một Knowledge Component (KC)
        dựa trên câu trả lời của học sinh (đúng/sai) và ghi vào file.
        """
        p_L_prev = self.mastery_vector.get(kc, self.p_L0)
        
        # Tính toán BKT Bayes
        p_correct_given_known = (1 - self.p_S)
        p_incorrect_given_known = self.p_S
        p_correct_given_unknown = self.p_G
        p_incorrect_given_unknown = (1 - self.p_G)

        p_observation = (p_L_prev * (p_correct_given_known if is_correct else p_incorrect_given_known)) + \
                        ((1 - p_L_prev) * (p_correct_given_unknown if is_correct else p_incorrect_given_unknown))

        if p_observation == 0:
            posterior_known = p_L_prev
        else:
            posterior_known = (p_L_prev * (p_correct_given_known if is_correct else p_incorrect_given_known)) / p_observation
        
        p_L_next = posterior_known + (1 - posterior_known) * self.p_T
        
        self.mastery_vector[kc] = max(0.0, min(1.0, p_L_next))

        # Ghi mastery_vector đã cập nhật vào file JSON
        self._save_mastery_to_file()

        # Thêm tương tác mới vào DataFrame và lưu vào file CSV
        new_interaction = pd.DataFrame([{
            'timestamp': datetime.datetime.now().isoformat(),
            'kc': kc,
            'is_correct': is_correct,
            'p_L_before': p_L_prev,
            'p_L_after': self.mastery_vector[kc]
        }])
        self.interactions_df = pd.concat([self.interactions_df, new_interaction], ignore_index=True)
        self._save_interactions_to_file()

    def get_mastery_vector(self) -> dict:
        """Trả về vector trình độ thành thạo hiện tại của học sinh (từ bộ nhớ, đã được sync với file)."""
        return self.mastery_vector

    def get_interactions_df(self) -> pd.DataFrame:
        """Trả về lịch sử tương tác dưới dạng DataFrame (từ bộ nhớ, đã được sync với file)."""
        return self.interactions_df

    def get_topic_stars(self) -> dict:
        topic_stars = {}
        for kc in self.all_kcs:
            mastery_level = self.mastery_vector.get(kc, self.p_L0)
            if mastery_level <= 0.2:
                topic_stars[kc] = 0
            elif mastery_level <= 0.4:
                topic_stars[kc] = 1
            elif mastery_level <= 0.6:
                topic_stars[kc] = 2
            elif mastery_level <= 0.8:
                topic_stars[kc] = 3
            elif mastery_level <= 0.9:
                topic_stars[kc] = 4
            else:
                topic_stars[kc] = 5
        return topic_stars

    def get_total_stars(self) -> int:
        topic_stars = self.get_topic_stars()
        total_stars = sum(topic_stars.values())
        return total_stars

    def get_current_title(self) -> str:
        total_stars = self.get_total_stars()
        
        if total_stars < 10:
            return "Người mới học"
        elif total_stars < 25:
            return "Người khám phá"
        elif total_stars < 40:
            return "Chuyên gia cơ bản"
        elif total_stars < 60:
            return "Thạc sĩ phân số"
        else:
            return "Đại kiện tướng phân số"