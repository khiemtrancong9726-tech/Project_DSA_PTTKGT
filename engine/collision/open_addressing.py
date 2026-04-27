# engine/collision/open_addressing.py

from engine.hash_table import HashTable


class OpenAddressingHashTable(HashTable):
    """
    Hash Table giải quyết collision bằng Open Addressing.

    Có 2 probe strategy — chỉnh comment để switch:
        [A] Linear Probing  — bước nhảy cố định +1, đơn giản, dễ cluster
        [B] Double Hashing  — bước nhảy theo h2(key), phân tán tốt hơn

    Complexity:
        insert : O(1) avg / O(n) worst
        search : O(1) avg / O(n) worst
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        self.table = [None] * self.size

        # ── [A] Linear Probing
        # ── không cần gì thêm ──

        # ── [B] Double Hashing — tính STEP_PRIME động theo size ──
        self.STEP_PRIME = self._find_step_prime()

    # ══════════════════════════════════════════════════════════════
    #  [B] Double Hashing helpers
    # ══════════════════════════════════════════════════════════════

    def _find_step_prime(self) -> int:
        n = self.size - 1
        while n > 1:
            if all(n % i != 0 for i in range(2, int(n**0.5) + 1)):
                return n
            n -= 1
        return 1

    def _hash2(self, key: str) -> int:
        """step = STEP_PRIME - (sum_ord % STEP_PRIME) → luôn ∈ [1, STEP_PRIME]."""
        raw = sum(ord(c) for c in key)
        return self.STEP_PRIME - (raw % self.STEP_PRIME)

    # ══════════════════════════════════════════════════════════════
    #  insert
    # ══════════════════════════════════════════════════════════════

    def insert(self, key: str, value: dict):
        if self.count >= self.size:
            raise OverflowError("Hash table đầy — không thể insert thêm.")

        idx = self._hash(key)

        # ── Chọn 1 trong 2 dòng dưới ──
        #step = self._hash2(key)   # [B] Double Hashing
        step = 1                # [A] Linear Probing

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                self.table[idx] = (key, value)
                self.count += 1
                return

            if slot[0] == key:
                self.table[idx] = (key, value)   # update in-place
                return

            idx = (idx + step) % self.size

        raise OverflowError("Hash table đầy — không thể insert thêm.")

    # ══════════════════════════════════════════════════════════════
    #  search
    # ══════════════════════════════════════════════════════════════

    def search(self, key: str):
        idx = self._hash(key)

        # ── Chọn 1 trong 2 dòng dưới ──
        #step = self._hash2(key)   # [B] Double Hashing
        step = 1                # [A] Linear Probing

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return None   # chắc chắn không có — dừng probe

            if slot[0] == key:
                return slot[1]

            idx = (idx + step) % self.size

        return None   # đã probe hết vòng