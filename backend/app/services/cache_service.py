class SimpleCache:
    def __init__(self):
        self._data: dict[str, object] = {}

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: object):
        self._data[key] = value


