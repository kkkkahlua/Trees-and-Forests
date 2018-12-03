# -*- coding:utf-8 -*-
from tree_node import TreeNode
import random
import numpy as np
from utils import euc_dist
from utils import vote_for_one

class CompTree(object):
    def __init__(self, n0):
        self.n0 = n0
        self.root = None
        self.task = "classification"

    def pick_two_samples(self, y):
        n_data = y.shape[0]

        left_idx = [i for i in range(n_data) if y[i] == y[0]]
        right_idx = [i for i in range(n_data) if i not in left_idx]

        assert len(left_idx) + len(right_idx) == n_data

        if not left_idx:
            idx = random.sample(range(len(right_idx)), 2)
            x0_idx = right_idx[idx[0]]
            x1_idx = right_idx[idx[1]]
        elif not right_idx:
            idx = random.sample(range(len(left_idx)), 2)
            x0_idx = left_idx[idx[0]]
            x1_idx = left_idx[idx[1]]
        else:
            x0_idx = left_idx[random.randint(0, len(left_idx)-1)]
            x1_idx = right_idx[random.randint(0, len(right_idx)-1)]
        return x0_idx, x1_idx

    def separate_samples(self, X, x0, x1):
        left_idx = []
        right_idx = []
        for idx, x in enumerate(X):
            if euc_dist(x, x0) <= euc_dist(x, x1):
                left_idx.append(idx)
            else:
                right_idx.append(idx)
        return left_idx, right_idx

    def build_tree(self, X, y):
        if X.shape[0] <= self.n0:
            return TreeNode(X, y, None, None, None, None)

        x0_idx, x1_idx = self.pick_two_samples(y)
        x0 = X[x0_idx]
        x1 = X[x1_idx]

        left_idx, right_idx = self.separate_samples(X, x0, x1)

        left_child = self.build_tree(X[left_idx], y[left_idx])
        right_child = self.build_tree(X[right_idx], y[right_idx])

        return TreeNode(X, y, x0, x1, left_child, right_child)
        # return TreeNode(X, y, x0, x1, left_child, right_child)

    def fit_transform(self, X, y):
        self.root = self.build_tree(X, y)

    def trace_in_tree(self, x):
        node = self.root
        while node.left_child is not None:
            if euc_dist(x, node.left_pivot) < euc_dist(x, node.right_pivot):
                node = node.left_child
            else:
                node = node.right_child
        return node
    
    def vote(self, leaf_node):
        return vote_for_one(leaf_node.y)

    def average(self, leaf_node):
        return sum(leaf_node.y) / len(leaf_node.y)

    def predict(self, X):
        y_predict = []
        for x in X:
            leaf_node = self.trace_in_tree(x)
            if (self.task == "classification"):
                y_predict.append(self.vote(leaf_node))
            else:
                y_predict.append(self.average(leaf_node))
        return np.array(y_predict)
        