from __future__ import annotations
import numpy as np
from .utils import get_nested_value, set_nested_value
from .config import CONSOLE
from random import randint
from collections.abc import Iterable


class KDTree:
    """
    k-dimensional binary search tree

    Attributes
    ----------
    leaf_size: int = 10
        Maximum number of data items per leaf.
    """

    def __init__(self, leaf_size: int = 10) -> None:
        self.leaf_size = leaf_size
        self.k = None
        self.min = None
        self.min = None
        self.norm = None
        self.data = None

    def __update_minmax(self, vector: np.ndarray) -> None:
        self.min = np.min(np.array([self.min, vector]), axis=0)
        self.max = np.max(np.array([self.max, vector]), axis=0)

    def __build(self, data: list, vector_path: str, k: int = 0) -> dict:
        data_size = len(data)
        if (data_size <= self.leaf_size):
            CONSOLE.bar.next(data_size)
            for d in data:
                self.__update_minmax(get_nested_value(d, vector_path))
            return {
                'leaf': data,
            }
        data.sort(key=lambda x: get_nested_value(x, vector_path)[k])
        middle_index = len(data) // 2
        next_k = (k + 1) % self.k
        vector = get_nested_value(data[middle_index], vector_path)
        return {
            'node': {
                'k': k,
                'value': vector[k]
            },
            0: self.__build(data[:middle_index], vector_path, next_k),
            1: self.__build(data[middle_index:], vector_path, next_k),
        }

    def build(self, data: list | np.ndarray, vector_path: str) -> None:
        # get tree dimensions
        self.k = len(get_nested_value(data[0], vector_path))

        # initialize min, max, and norm arrays
        self.min = np.zeros(self.k)
        self.min.fill(np.inf)

        self.max = np.zeros(self.k)
        self.max.fill(-np.inf)

        self.norm = np.ones(self.k)

        CONSOLE.reset_bar('Classifying audio grains:', max=len(data), item='grains')
        # build binary tree and fit data
        self.data = self.__build(data, vector_path, k=randint(0, self.k-1))
        CONSOLE.bar.finish()
        self.norm = self.max - self.min
        self.__fit(vector_path)

    def __normalize_input(self, x: np.ndarray) -> np.ndarray:
        return (x - self.min) / self.norm

    def __fit(self, vector_path: str) -> None:
        """ recursively normalize tree data """
        def fit(tree, vector_path):
            if 'node' in tree:
                k = tree['node']['k']
                tree['node']['value'] = (
                    tree['node']['value'] - self.min[k]) / self.norm[k]
                fit(tree[0], vector_path)
                fit(tree[1], vector_path)
                return
            for leaf_item in tree['leaf']:
                vector = get_nested_value(leaf_item, vector_path)
                set_nested_value(leaf_item, vector_path,
                                 self.__normalize_input(vector))
        fit(self.data, vector_path)

    def __euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return np.sqrt(np.sum((a-b)**2))

    def knn(self, x: np.ndarray, vector_path: str, first_n: int = 10) -> Iterable:
        data = self.data
        data_point = self.__normalize_input(x)
        while 'node' in data:
            node = data['node']
            data = data[int(data_point[node['k']] >= node['value'])]
        return sorted(
            [
                {
                    'cost': self.__euclidean_distance(
                        data_point,
                        get_nested_value(leaf_item, vector_path)),
                    'value': leaf_item
                } for leaf_item in data['leaf']
            ], key=lambda x: x['cost'])[:first_n]

    def read(self, tree: dict) -> None:
        for attr in tree:
            hasattr(self, attr) and setattr(self, attr, tree[attr])
