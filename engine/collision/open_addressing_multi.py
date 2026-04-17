# engine/collision/open_addressing_multi.py

from engine.collision.open_addressing import OpenAddressingHashTable


class OpenAddressingMultiHashTable(OpenAddressingHashTable):
    """
    Open Addressing Hash Table cho bài toán 1 key → nhiều value.
    Kế thừa OpenAddressingHashTable — tái dụng Double Hashing hoàn toàn.

    Complexity:
        insert : O(1) avg
        search : O(1) avg — trả về list toàn bộ record của key đó
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        self.table = [None] * self.size

    def insert(self, key: str, value: dict):
        idx  = self._hash(key)
        step = self._hash2(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                self.table[idx] = (key, [value])
                self.count += 1
                return

            if slot[0] == key:
                slot[1].append(value)
                return

            idx = (idx + step) % self.size

        raise OverflowError("Hash table đầy — không thể insert thêm.")

    def search(self, key: str):
        idx  = self._hash(key)
        step = self._hash2(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return []

            if slot[0] == key:
                return slot[1]

            idx = (idx + step) % self.size

        return []