import numpy as np
from typing import Any


def get_nested_value(obj: object, path: str | None, separator: str = ".") -> Any:
    """
    Helper function to get an a nested value from an ``object`` of aribirary depth

    obj: object
        Object to extract value from.

    path: str | None
        path to traverse ``obj``, separated by ``separator``.

    separator: str
        substring by which to parse ``path``
    """
    output = obj
    for key in path.split(separator):
        t = type(output)
        if t == list:
            output = output[int(key)]
        elif t == dict:
            output = output[key]
        else:
            output = getattr(output, key)
    return output


def __set_nested_value(obj, paths, replace):
    if not paths:
        obj = replace
        return obj
    k = paths[0]
    if isinstance(obj, list) or isinstance(obj, np.ndarray):
        obj[int(k)] = __set_nested_value(obj[int(k)], paths[1:], replace)
    elif isinstance(obj, dict):
        obj[k] = __set_nested_value(obj[k], paths[1:], replace)
    else:
        setattr(obj, k, __set_nested_value(getattr(obj, k), paths[1:], replace))
    return obj


def set_nested_value(obj, path, replace, separator: str = '.') -> Any:
    """
    Helper function to update an a nested value from an ``object`` of aribirary depth

    obj: object
        Object to extract value from.

    replace:

    path: str | None
        path to traverse ``obj``, separated by ``separator``.

    separator: str
        substring by which to parse ``path``
    """
    return __set_nested_value(obj, path.split(separator), replace)


def resample_array(array, N):
    return np.interp(np.linspace(0, len(array) - 1, N), np.arange(0, len(array)), array)
