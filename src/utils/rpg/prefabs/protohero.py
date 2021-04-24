import textwrap

from utils.rpg.piece import Being, DefiniteSkin

characters = {
    "Yuni": 828629768651014195,
    "Yui": 828630740341227570,
    "Pecorine": 828630739871858719,
    "Luna": 828110282823434281,
    "Kyaru": 828630740123779072,
}
__all__ = [f"Prototype{name}" for name in characters]

for _ in characters:
    exec(
        textwrap.dedent(
            f"""
            class Prototype{_}(Being):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.skin = DefiniteSkin([["<:__:{characters[_]}>"]])
            """
        )
    )
