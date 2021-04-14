from typing import Tuple
import random
import random
import math


class RRT:
    class Node:   # 节点类，每个节点都存储了从父节点到当前节点的完整路径
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.path_x = []  # to define the path from parent to current---
            self.path_y = []  # the purpose is to check collision of the path
            self.parent = None

    def __init__(self,
                 boundary: Tuple[int, int, int, int],
                 goal: Tuple[int, int],
                 seed: int = 1,
                 goal_sample_rate: int = 5,
                 step: int = 30):
        random.seed(seed)
        self.node_list = []
        self.goal_sample_rate = goal_sample_rate
        self.boundary = boundary
        self.goal = goal
        self.step = step  # 每一步定向生长的长度

    def get_a_point(self) -> Tuple[int, int, int, int]:
        """x1, y1, x2, y2"""
        rnd_node = self.get_random_node()
        nearest_node = self.get_nearest_node_node(self.node_list, rnd_node)  # 找到树上距离随机点最近的节点
        x1, y1 = nearest_node.x, nearest_node.y
        x2_, y2_ = rnd_node.x, rnd_node.y
        dis = math.sqrt((x2_ - x1)**2 + (y2_ - y1)**2)
        scale = self.step / dis
        x2 = round(x1+(x2_-x1)*scale)
        y2 = round(y1+(y2_-y1)*scale)
        return x1, y1, x2, y2

    def get_random_node(self):
        if random.randint(0, 100) > self.goal_sample_rate:
            rnd = self.Node(random.uniform(self.boundary[0], self.boundary[2]),
                            random.uniform(self.boundary[1], self.boundary[3]))
        else:  # goal point sampling
            rnd = self.Node(self.goal[0], self.goal[1])
        return rnd


    def update(self, x: int, y: int, collide: bool):
        if not collide:
            self.node_list.append((x, y))

    # @staticmethod
    def get_nearest_node_node(self, rnd_node: Node) -> Node:        # 找最近节点
        dlist = [(node.x - rnd_node.x) ** 2 + (node.y - rnd_node.y)
                 ** 2 for node in self.node_list]
        minind = dlist.index(min(dlist))

        return self.node_list[minind]
