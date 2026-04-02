# engine/collision/open_addressing.py

from engine.hash_table import HashTable


class OpenAddressingHashTable(HashTable):
    """
    Hash Table giải quyết collision bằng Open Addressing — Linear Probing.

    Khi bucket bị chiếm → thử bucket kế tiếp: (idx + 1) % size.
    Toàn bộ data nằm trong 1 mảng phẳng, không dùng list phụ.

    Complexity:
        insert : O(1) avg / O(n) worst
        search : O(1) avg / O(n) worst

    Giới hạn load factor:
        Open Addressing bắt buộc α < 1 (không thể có nhiều phần tử hơn slot).
        α > 0.7 → probe length tăng mạnh → hiệu năng giảm rõ rệt.
        Thực tế nên giữ α ≤ 0.6 cho Linear Probing.
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        # Mỗi slot: None (trống) | (key, value)
        self.table = [None] * self.size

    # ---- insert ----

    def insert(self, key: str, value: dict):
        """
        Thêm (key, value) vào bảng.
        Nếu key đã tồn tại → update value.
        """
        if self.count >= self.size:
            raise OverflowError("Hash table đầy — không thể insert thêm.")

        idx = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                self.table[idx] = (key, value)
                self.count += 1
                return

            if slot[0] == key:
                # Key đã tồn tại → update in-place
                self.table[idx] = (key, value)
                return

            idx = (idx + 1) % self.size   # linear probe

        raise OverflowError("Hash table đầy — không thể insert thêm.")

    # ---- search ----

    def search(self, key: str):
        """
        Tìm kiếm theo key.
        Trả về value nếu tìm thấy, None nếu không có.

        Probe dừng khi gặp None (slot chưa từng bị dùng).
        """
        idx = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return None   # chắc chắn không có — dừng probe

            if slot[0] == key:
                return slot[1]   # tìm thấy

            idx = (idx + 1) % self.size

        return None   # đã probe hết vòng

    # ---- debug helper ----

    def probe_length(self, key: str) -> int:
        """
        Đếm số bước probe cần thiết để tìm key.
        Dùng để visualize clustering khi α tăng cao.
        """
        idx = self._hash(key)
        steps = 0

        for _ in range(self.size):
            slot = self.table[idx]
            steps += 1

            if slot is None:
                return steps   # không tìm thấy nhưng vẫn trả về số bước

            if slot[0] == key:
                return steps

            idx = (idx + 1) % self.size

        return steps