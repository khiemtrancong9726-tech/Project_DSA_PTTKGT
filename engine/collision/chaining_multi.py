# engine/collision/chaining_multi.py

from engine.hash_table import HashTable


class ChainingMultiHashTable(HashTable):
    """
    Chaining Hash Table cho bài toán 1 key → nhiều value.

    Khác ChainingHashTable ở đúng 1 điểm:
    insert gặp key trùng → append vào list, KHÔNG ghi đè.

    Dùng cho Scenario 2A — key là composite "department_code_gpa",
    value là list tất cả record thuộc cùng khoa và GPA đó.

    Complexity:
        insert : O(1) avg
        search : O(1) avg — trả về list toàn bộ record của key đó
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        self.table = [[] for _ in range(self.size)]

    def insert(self, key: str, value: dict):
        idx   = self._hash(key)
        chain = self.table[idx]

        for k, v in chain:
            if k == key:
                v.append(value)  # key đã có → append vào list, không ghi đè
                return

        chain.append((key, [value]))  # key mới → tạo list mới
        self.count += 1

    def search(self, key: str):
        idx   = self._hash(key)
        chain = self.table[idx]

        for k, v in chain:
            if k == key:
                return v  # trả về list các record

        return []  # không tìm thấy → list rỗng