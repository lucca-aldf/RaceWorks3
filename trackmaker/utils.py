from typing import Tuple

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_BACKGROUND = (20, 150, 20)
COLOR_TRACK = (96, 96, 96)

def add_tuples(*tuples:Tuple[Tuple, Tuple]):
    size = len(tuples[0])
    result = [0 for _ in range(size)]

    for tuple_ in tuples:
        for i in range(size):
            result[i] += tuple_[i]
    
    return tuple(result)


def subtract_tuples(first_tuple:Tuple, second_tuple:Tuple, size:int=2):
    size = len(first_tuple)
    result = [0 for _ in range(size)]

    for i in range(size):
        result[i] += first_tuple[i]
    for i in range(size):
        result[i] -= second_tuple[i]
    
    return tuple(result)


def multiply_tuple(tuple_:Tuple, scale:int):
    return (tuple_[0] * scale, tuple_[1] * scale)