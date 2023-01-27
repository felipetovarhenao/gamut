import numpy as np
from progress.bar import IncrementalBar
from .utils import inspect_object, deep_update
from .config import LOGGER
from random import randint


class KDTree:
    """
    k-Dimensional Binary Search Tree 

    Attributes
    ----------
    leaf_size: int = 10
        Maximum number of data items per leaf.

    Methods
    ----------
    build(data: list | np.ndarray, vector_path: str) -> None:
        builds tree from `data`.

    knn(x: np.ndarray, vector_path: str, first_n: int = 1):
        find `first_n` matches, based on `x`.

    read(tree: dict) -> None:
        re-initialize class members from `tree`.
    """

    def __init__(self, leaf_size: int = 10) -> None:
        self.leaf_size = leaf_size
        self.k = None
        self.min = None
        self.min = None
        self.norm = None
        self.data = None
        self.bar = None

    def __update_minmax(self, vector: np.ndarray) -> None:
        self.min = np.min(np.array([self.min, vector]), axis=0)
        self.max = np.max(np.array([self.max, vector]), axis=0)

    def __build(self, data: list, vector_path: str, k: int = 0) -> dict:
        data_size = len(data)
        if (data_size <= self.leaf_size):
            self.bar.next(data_size)
            for d in data:
                self.__update_minmax(inspect_object(d, vector_path))
            return {
                'leaf': data,
            }
        data.sort(key=lambda x: inspect_object(x, vector_path)[k])
        middle_index = len(data) // 2
        next_k = (k + 1) % self.k
        vector = inspect_object(data[middle_index], vector_path)
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
        self.k = len(inspect_object(data[0], vector_path))

        # initialize min, max, and norm arrays
        self.min = np.zeros(self.k)
        self.min.fill(np.inf)

        self.max = np.zeros(self.k)
        self.max.fill(-np.inf)

        self.norm = np.ones(self.k)

        self.bar = IncrementalBar(LOGGER.subprocess(
            'Classifying audio grains: '), max=len(data), suffix='%(index)d/%(max)d grains')

        # build binary tree and fit data
        self.data = self.__build(data, vector_path, k=randint(0, self.k-1))
        self.bar.finish()
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
                vector = inspect_object(leaf_item, vector_path)
                deep_update(leaf_item, vector_path,
                            self.__normalize_input(vector))
        fit(self.data, vector_path)

    def __euclidean_distance(self, a, b):
        return np.sqrt(np.sum((a-b)**2))

    def knn(self, x: np.ndarray, vector_path: str, first_n: int = 10) -> list:
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
                        inspect_object(leaf_item, vector_path)),
                    'value': leaf_item
                } for leaf_item in data['leaf']
            ], key=lambda x: x['cost'])[:first_n]

    def read(self, tree: dict) -> None:
        for attr in tree:
            hasattr(self, attr) and setattr(self, attr, tree[attr])
