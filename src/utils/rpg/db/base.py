from uuid import UUID


class BaseData(object):
    __slots__ = ("identifier",)

    def __init__(self, identifier: UUID):
        self.identifier = identifier
