# app/core/store.py

from collections import OrderedDict


class LRUStore:
    def __init__(self, max_size=100):
        self.store = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.store:
            self.store.move_to_end(key)
            return self.store[key]
        return None

    def set(self, key, value):
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = value
        if len(self.store) > self.max_size:
            self.store.popitem(last=False)


session_info_store = LRUStore(max_size=100)
chat_history_store = LRUStore(max_size=100)
