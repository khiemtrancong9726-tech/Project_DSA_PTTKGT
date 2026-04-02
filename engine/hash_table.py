# engine/hash_table.py

# Sentinel dùng cho Open Addressing — phân biệt "chưa có" vs "đã xóa"
# Đặt ở module level để chaining.py và open_addressing.py đều import được
DELETED = object()


class HashTable:
    """
    Base class — định nghĩa interface chung cho mọi loại hash table.
    Chaining và Open Addressing đều kế thừa từ class này.
    """

    def __init__(self, size: int = 1009):
        self.size  = size                  # kích thước bảng — dùng số nguyên tố
        self.table = [None] * self.size    # mảng các bucket
        self.count = 0                     # số phần tử hiện có

    # ---- Hash function ----

    def _hash(self, key: str) -> int:
        """
        Chuyển student_id (CCCD string) → chỉ số bucket.

        Dùng Polynomial Rolling Hash — đọc toàn bộ ký tự,
        không bỏ sót prefix → tránh clustered collision.

        Không dùng hash() built-in vì Python 3.3+ thêm random seed
        mỗi lần chạy → kết quả không deterministic → benchmark sai.
        """
        h = 0
        for char in key:
            h = (h * 31 + ord(char)) % self.size
        return h

    # ---- Interface bắt buộc — subclass PHẢI override ----

    def insert(self, key: str, value: dict):
        raise NotImplementedError

    def search(self, key: str):
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    # ---- Thông tin trạng thái ----

    def load_factor(self) -> float:
        """
        Tỉ lệ phần tử / kích thước bảng.
        α > 0.7 → collision tăng mạnh → lookup bắt đầu degradation.
        Dùng trong load factor experiment của Scenario 1.
        """
        return self.count / self.size

    def __len__(self) -> int:
        return self.count