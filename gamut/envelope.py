import numpy as np


class Envelope:

    def __init__(self, points: list) -> None:
        pass

    def __clean_points(self, points):
        if type(points) not in [np.ndarray, list]:
            raise ValueError(f'{points} must be a list of numbers')
