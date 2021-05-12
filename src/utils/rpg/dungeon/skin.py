from numbers import Number
from typing import Iterable


class Skin:
    def get_index(self, x: Number, y: Number):
        raise NotImplementedError

    def get_bounds(self):
        raise NotImplementedError


class DefiniteSkin(Skin, object):
    __slots__ = ("_skin",)

    def __init__(self, skin: Iterable[Iterable[str]]):
        self._skin = skin
        self._skin.reverse()

    def get_bounds(self):
        return (range(len(self._skin[0])), range(len(self._skin)))

    def get_index(self, x: Number, y: Number):
        bounds = self.get_bounds()
        if y not in bounds[1] or x not in bounds[0]:
            return None
        return self._skin[int(y)][int(x)]
