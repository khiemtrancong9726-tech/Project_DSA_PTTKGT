# engine/inverted_index.py

from engine.collision.chaining_multi import ChainingMultiHashTable
from engine.fuzzy_search import normalize


class InvertedIndex:

    def __init__(self, size: int = 97):  # next_prime(48 * 2) — 48 token unique cố định
        self.index = ChainingMultiHashTable(size=size)

    def build(self, records: list):
        for record in records:
            tokens = normalize(record["name"]).split()
            for token in tokens:
                self.index.insert(token, record)

    def search(self, query: str) -> list:
        tokens = normalize(query).strip().split()
        if not tokens:
            return []

        # 1 token → tra thẳng
        if len(tokens) == 1:
            return self.index.search(tokens[0])

        # nhiều token → intersect theo student_id
        sets = [
            {r["student_id"]: r for r in self.index.search(t)}
            for t in tokens
        ]
        common_ids = set(sets[0]).intersection(*sets[1:])
        return [sets[0][sid] for sid in common_ids]