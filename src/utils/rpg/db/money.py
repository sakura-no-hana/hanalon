from numbers import Number
import textwrap


class Money:
    DENOMINATIONS = {"copper": 0, "silver": 2, "gold": 4, "platinum": 6}

    def __init__(self, amount: Number = 0):
        self.amount = amount

    def _get(self, scale: int):
        return self.amount % 10 ** (scale + 2) // 10 ** scale

    def _set(self, scale: int, amount: Number):
        self.amount += 10 ** scale * amount - self._get(scale)

    for coin in DENOMINATIONS:
        exec(
            textwrap.dedent(
                f"""
                @property
                def {coin}(self):
                    return self._get({DENOMINATIONS[coin]})

                @{coin}.setter
                def {coin}(self, amount):
                    self._set({DENOMINATIONS[coin]}, amount)
                """
            )
        )
