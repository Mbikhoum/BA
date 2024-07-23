# 1. Array
class Array:
    def __init__(self):
        self.array = []

    def insert(self, value):
        self.array.append(value)

    def delete(self, value):
        try:
            self.array.remove(value)
        except ValueError:
            pass  # Value not found, do nothing

    def search(self, value):
        return value in self.array


# 2. Queue
class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        return None

    def is_empty(self):
        return len(self.queue) == 0


# 3. Binary Search Tree
class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.value = key

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
        else:
            self._insert(self.root, key)

    def _insert(self, root, key):
        if key < root.value:
            if root.left is None:
                root.left = Node(key)
            else:
                self._insert(root.left, key)
        else:
            if root.right is None:
                root.right = Node(key)
            else:
                self._insert(root.right, key)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, root, key):
        if root is None:
            return None
        if root.value == key:
            return root
        if key < root.value:
            return self._search(root.left, key)
        return self._search(root.right, key)


# 4. Linked List
class LinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        new_node = LinkedListNode(data)
        new_node.next = self.head
        self.head = new_node

    def search(self, key):
        current = self.head
        while current:
            if current.data == key:
                return True
            current = current.next
        return False

    def delete(self, key):
        current = self.head
        prev = None
        while current and current.data != key:
            prev = current
            current = current.next
        if current is None:
            return  # Key not found, do nothing
        if prev is None:
            self.head = current.next
        else:
            prev.next = current.next


# 5. Hashed Tree (Merkle Tree)
import hashlib

class MerkleTree:
    def __init__(self, data):
        self.data = data
        self.tree = []
        self.build_tree()

    def build_tree(self):
        nodes = [self.hash_leaf(x) for x in self.data]
        while len(nodes) > 1:
            temp_nodes = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                temp_nodes.append(self.hash_internal_node(left, right))
            nodes = temp_nodes
        self.tree = nodes

    def hash_leaf(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def hash_internal_node(self, left, right):
        return hashlib.sha256((left + right).encode('utf-8')).hexdigest()

    def get_root(self):
        return self.tree[0] if self.tree else None


# 6. Stack
class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def is_empty(self):
        return len(self.stack) == 0


# 7. Graph (Adjacency List)
class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        self.graph[u].append(v)  # This allows multiple edges to the same node

    def get_adjacent_nodes(self, u):
        return self.graph.get(u, [])


# 8. Tree (Generic Tree)
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Tree:
    def __init__(self, root):
        self.root = root

    def search(self, node, value):
        if node.data == value:
            return node
        for child in node.children:
            result = self.search(child, value)
            if result:
                return result
        return None
