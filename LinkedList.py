"""
Linked List data structure
"""
__author__ = "Srikanth Mantravadi"
__email__ = "sxm6373@psu.edu"

import logging as lg
lg.basicConfig(level=lg.DEBUG)


class LLNode:
    next = None
    data = None

    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next


class LinkedList:
    head: LLNode

    def __init__(self):
        self.head = None
        return self.head

    def add(self, data):
        newnode = LLNode()
        newnode.next = self.head
        newnode.data = data
        self.head = newnode

    def find(self, key: int):
        node = self.head
        while node:
            if node.data.get('key') == key:
                return node
            node = node.next

        return node

    def printlist(self):
        node = self.head
        while node:
            print(node.data)
            node = node.next

    def clear(self):
        self.head = None