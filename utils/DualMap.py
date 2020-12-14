from bidict import bidict


class DualMap:
    def __init__(self, data, unknown=(None, None)):
        self.__map = bidict(data)
        self.__unknown_key = unknown[0]
        self.__unknown_value = unknown[1]

    def is_valid_key(self, key):
        return key in self.__map

    def to_key(self, value):
        return self.__map.inverse.get(value, default=self.__unknown_key)

    def is_valid_value(self, value):
        return value in self.__map.inverse

    def to_value(self, key):
        return self.__map.get(key, default=self.__unknown_value)

    def to_key_either(self, value):
        if self.is_valid_key(value):
            return value

        if self.is_valid_value(value):
            return self.to_key(value)

        return self.__unknown_key

    def values(self):
        return self.__map.values()

    def keys(self):
        return self.__map.keys()

    def minimum_key(self):
        return min(self.__map.keys())

    def maximum_key(self):
        return max(self.__map.keys())

    def to_dict(self):
        return {k: v for k, v in self.__map.items()}

    def to_reverse_dict(self):
        return {v: k for k, v in self.__map.items()}
