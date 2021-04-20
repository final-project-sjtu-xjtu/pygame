from typing import Tuple
import random
import random
import math
import cv2
import numpy as np


class RRT:
    class Node:   # 节点类，每个节点都存储了从父节点到当前节点的完整路径
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.parent = None
            self.child = []

    class Stack:
        def __init__(self):
            self.items = []

        def is_empty(self):
            return self.items == []

        def push(self, item):
            self.items.append(item)

        def pop(self):
            return self.items.pop()

        def peek(self):
            return self.items[len(self.items) - 1]

        def size(self):
            return len(self.items)

    def __init__(self,
                 boundary: Tuple[int, int, int, int],
                 goal: Tuple[int, int],
                 start_point: Tuple[int, int],
                 seed: int = 1,
                 goal_sample_rate: int = 5,
                 step: int = 30):
        random.seed(seed)
        start_node = self.Node(*start_point)
        self.node_list = [start_node]
        self.goal_sample_rate = goal_sample_rate
        self.boundary = boundary
        self.goal = goal
        self.step = step  # 每一步定向生长的长度

    def get_a_point(self) -> Tuple[int, int, int, int, Node]:
        """x1, y1, x2, y2"""
        rnd_node = self.get_random_node()
        nearest_node = self.get_nearest_node_node(rnd_node)  # 找到树上距离随机点最近的节点
        x1, y1 = nearest_node.x, nearest_node.y
        x2_, y2_ = rnd_node.x, rnd_node.y
        dis = math.sqrt((x2_ - x1)**2 + (y2_ - y1)**2)
        scale = self.step / dis
        x2 = round(x1+(x2_-x1)*scale)
        y2 = round(y1+(y2_-y1)*scale)
        return x1, y1, x2, y2, nearest_node

    def update(self, x: int, y: int, nearest_node: Node, collide: bool):
        if not collide:
            node = self.Node(x, y)
            node.parent = nearest_node
            self.node_list.append(node)
            nearest_node.child.append(node)

    def get_random_node(self):
        if random.randint(0, 100) > self.goal_sample_rate:
            rnd = self.Node(random.uniform(self.boundary[0], self.boundary[2]),
                            random.uniform(self.boundary[1], self.boundary[3]))
        else:  # goal point sampling
            rnd = self.Node(self.goal[0], self.goal[1])
        return rnd

    def get_nearest_node_node(self, rnd_node: Node) -> Node:        # 找最近节点
        dlist = [(node.x - rnd_node.x) ** 2 + (node.y - rnd_node.y)
                 ** 2 for node in self.node_list]
        minind = dlist.index(min(dlist))

        return self.node_list[minind]

    def potential_field_map_generator(self, root_node: Node, map_width, map_height):
        node_stack = self.Stack()
        pfmap_size = (map_width, map_height, 3)
        pfmap = np.ones(pfmap_size) * 255
        node_stack.push(root_node)
        linethickness = 1
        radius = 5
        while node_stack.size() > 0:
            node = node_stack.pop()
            cv2.circle(pfmap, (node.x, node.y), radius, (0, 0, 255), -1)
            if node.child:
                for i in node.child:
                    node_stack.push(i)
            if node.parent:
                print("yes")
                cv2.line(pfmap, (node.x, node.y), (node.parent.x, node.parent.y), (0, 0, 0), linethickness)
        cv2.imshow('pfmap', pfmap)
        cv2.waitKey()
