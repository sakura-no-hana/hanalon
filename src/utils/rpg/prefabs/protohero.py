from utils.rpg.pieces import Being, DefiniteSkin

_characters = {
    "Yuni": 828629768651014195,
    "Yui": 828630740341227570,
    "Pecorine": 828630739871858719,
    "Luna": 828110282823434281,
    "Kyaru": 828630740123779072,
}
__all__ = [f"Prototype{name}" for name in _characters]

for _ in _characters:
    exec(
        f"""
class Prototype{_}(Being):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skin = DefiniteSkin([["<:__:{_characters[_]}>"]])
    """
    )
