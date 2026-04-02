# engine/collision/open_addressing.py

from engine.hash_table import HashTable, DELETED


class OpenAddressingHashTable(HashTable):
    """
    Hash Table giải quyết collision bằng Open Addressing — Linear Probing.

    Khi bucket bị chiếm → thử bucket kế tiếp: (idx + 1) % size.
    Toàn bộ data nằm trong 1 mảng phẳng, không dùng list phụ.

    Complexity:
        insert : O(1) avg / O(n) worst
        search : O(1) avg / O(n) worst
        delete : O(1) avg / O(n) worst  — dùng tombstone, KHÔNG xóa thật

    Tombstone (DELETED sentinel):
        Nếu xóa thật (set None), search sau đó sẽ dừng sớm tại slot None
        và miss các key đã probe qua slot đó trước khi bị xóa.
        → Phải để lại DELETED để probe tiếp tục, nhưng insert được ghi đè.

    Giới hạn load factor:
        Open Addressing bắt buộc α < 1 (không thể có nhiều phần tử hơn slot).
        α > 0.7 → probe length tăng mạnh → hiệu năng giảm rõ rệt.
        Thực tế nên giữ α ≤ 0.6 cho Linear Probing.
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        # Mỗi slot: None (trống) | DELETED (tombstone) | (key, value)
        self.table = [None] * self.size

    # ---- insert ----

    def insert(self, key: str, value: dict):
        """
        Thêm (key, value) vào bảng.
        Nếu key đã tồn tại → update value.
        Nếu gặp DELETED trong khi probe → ghi vào slot đó (tái sử dụng).
        """
        if self.count >= self.size:
            raise OverflowError("Hash table đầy — không thể insert thêm.")

        idx = self._hash(key)
        first_deleted = None   # vị trí DELETED đầu tiên gặp trong probe

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                # Slot trống — ghi vào đây (hoặc vào first_deleted nếu đã thấy)
                target = first_deleted if first_deleted is not None else idx
                self.table[target] = (key, value)
                self.count += 1
                return

            if slot is DELETED:
                # Ghi nhớ vị trí tombstone đầu tiên — có thể tái dùng
                if first_deleted is None:
                    first_deleted = idx

            elif slot[0] == key:
                # Key đã tồn tại → update in-place
                self.table[idx] = (key, value)
                return

            idx = (idx + 1) % self.size   # linear probe

        # Đã probe hết vòng mà không tìm thấy None → dùng first_deleted
        if first_deleted is not None:
            self.table[first_deleted] = (key, value)
            self.count += 1
        else:
            raise OverflowError("Hash table đầy — không thể insert thêm.")

    # ---- search ----

    def search(self, key: str):
        """
        Tìm kiếm theo key.
        Trả về value nếu tìm thấy, None nếu không có.

        Probe dừng khi gặp None (slot chưa từng bị dùng).
        KHÔNG dừng khi gặp DELETED — phải tiếp tục probe qua tombstone.
        """
        idx = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return None   # chắc chắn không có — dừng probe

            if slot is not DELETED and slot[0] == key:
                return slot[1]   # tìm thấy

            idx = (idx + 1) % self.size   # tiếp tục probe qua DELETED

        return None   # đã probe hết vòng

    # ---- delete ----

    def delete(self, key: str) -> bool:
        """
        Xóa phần tử theo key bằng cách để lại tombstone DELETED.
        Trả về True nếu xóa thành công, False nếu key không tồn tại.

        KHÔNG set slot về None — làm vậy sẽ cắt đứt probe chain
        và khiến search miss các key phía sau.
        """
        idx = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return False   # key không tồn tại

            if slot is not DELETED and slot[0] == key:
                self.table[idx] = DELETED   # tombstone — giữ probe chain
                self.count -= 1
                return True

            idx = (idx + 1) % self.size

        return False   # đã probe hết vòng

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

            if slot is not DELETED and slot[0] == key:
                return steps

            idx = (idx + 1) % self.size

        return steps