import pygame
import io


def LoadSVG(filename:str, x=1, y=1) -> pygame.Surface:
    """
    LoadSVG(filename, x=1, y=1)

    filename: path to svg    : str
    x           : attitude width : int | float
    y           : attitude height: int | float
    """
    with open(filename, "rt") as f:
        svg_string = f.read()
    start = svg_string.find('<svg')
    if start:
        svg_string = svg_string[:start+4] + f' transform="scale({x}, {y})"' + svg_string[start+4:]
        return pygame.image.load(io.BytesIO(svg_string.encode()))

