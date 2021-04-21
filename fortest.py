import cv2
import numpy as np
from RRT.RRT import RRT


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


def potential_field_map_generator(root_node, map_width, map_height):
    node_stack = Stack()
    pfmap_size = (map_width, map_height, 3)
    pfmap = np.ones(pfmap_size) * 255
    node_stack.push(root_node)
    linethickness = 2
    while node_stack.size() > 0:
        node = node_stack.pop()
        cv2.circle(pfmap, (node.x, node.y), 5, (0, 0, 255), -1)
        if node.child:
            for i in node.child:
                node_stack.push(i)
        if node.parent:  # 只有根结点不用画
            print("yes")
            cv2.line(pfmap, (node.x, node.y), (node.parent.x, node.parent.y), (0, 0, 0), linethickness)

        print(node_stack.items)
    # cv2.imshow('pfmap', pfmap)
    return pfmap
    # cv2.waitKey()


def test():
    n1 = RRT.Node(50, 0)
    n11 = RRT.Node(25, 50)
    n12 = RRT.Node(75, 50)
    n121 = RRT.Node(50, 100)
    n122 = RRT.Node(100, 100)

    n1.child.append(n11)
    n1.child.append(n12)
    n11.parent = n1
    n12.parent = n1
    n12.child.append(n121)
    n12.child.append(n122)
    n121.parent = n12
    n122.parent = n12
    rrt = RRT((0, 0, 0, 0), (0, 0), (0, 0))
    return rrt.potential_field_map_generator(n1, 150, 150, 150, 150)


if __name__ == '__main__':
    pic = test()
    cv2.imshow("pic", pic)
    cv2.waitKey()

