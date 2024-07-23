import os
import hypothesis.strategies as st
from hypothesis import given
from main import *
import pytest

def generate_tests():
    test_file = open("test_main.py", "w")
    test_file.write("import hypothesis.strategies as st\n")
    test_file.write("from hypothesis import given\n")
    test_file.write("from main import *\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_Array_insert_delete_search(array_values):\n")
    test_file.write("    arr = Array()\n")
    test_file.write("    seen_values = set()\n")
    test_file.write("    for value in array_values:\n")
    test_file.write("        if value not in seen_values:\n")
    test_file.write("            arr.insert(value)\n")
    test_file.write("            seen_values.add(value)\n")
    test_file.write("    for value in seen_values:\n")
    test_file.write("        assert arr.search(value) == True\n")
    test_file.write("        arr.delete(value)\n")
    test_file.write("        assert arr.search(value) == False\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_Queue_enqueue_dequeue(queue_values):\n")
    test_file.write("    queue = Queue()\n")
    test_file.write("    for value in queue_values:\n")
    test_file.write("        queue.enqueue(value)\n")
    test_file.write("    for value in queue_values:\n")
    test_file.write("        assert queue.dequeue() == value\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_BinarySearchTree_insert_search(bst_values):\n")
    test_file.write("    bst = BinarySearchTree()\n")
    test_file.write("    for value in bst_values:\n")
    test_file.write("        bst.insert(value)\n")
    test_file.write("    for value in bst_values:\n")
    test_file.write("        assert bst.search(value) is not None\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_LinkedList_insert_search_delete(ll_values):\n")
    test_file.write("    ll = LinkedList()\n")
    test_file.write("    seen_values = set()\n")
    test_file.write("    for value in ll_values:\n")
    test_file.write("        if value not in seen_values:\n")
    test_file.write("            ll.insert(value)\n")
    test_file.write("            seen_values.add(value)\n")
    test_file.write("    for value in seen_values:\n")
    test_file.write("        assert ll.search(value) == True\n")
    test_file.write("        ll.delete(value)\n")
    test_file.write("        assert ll.search(value) == False\n\n")

    test_file.write("@given(st.lists(st.text()))\n")
    test_file.write("def test_MerkleTree_build_tree(mt_values):\n")
    test_file.write("    mt = MerkleTree(mt_values)\n")
    test_file.write("    assert mt.tree is not None\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_Stack_push_pop(stack_values):\n")
    test_file.write("    stack = Stack()\n")
    test_file.write("    for value in stack_values:\n")
    test_file.write("        stack.push(value)\n")
    test_file.write("    for value in reversed(stack_values):\n")
    test_file.write("        assert stack.pop() == value\n\n")

    test_file.write("@given(st.lists(st.integers()), st.lists(st.integers()))\n")
    test_file.write("def test_Graph_add_edge_get_adjacent_nodes(graph_values, edge_values):\n")
    test_file.write("    graph = Graph()\n")
    test_file.write("    for u, v in zip(graph_values, edge_values):\n")
    test_file.write("        graph.add_edge(u, v)\n")
    test_file.write("    for u in graph_values:\n")
    test_file.write("        expected = [v for (src, v) in zip(graph_values, edge_values) if src == u]\n")
    test_file.write("        assert sorted(graph.get_adjacent_nodes(u)) == sorted(expected)\n\n")

    test_file.write("@given(st.lists(st.integers()))\n")
    test_file.write("def test_Tree_search(tree_values):\n")
    test_file.write("    if not tree_values:\n")
    test_file.write("        return  # Skip test if no values are provided\n")
    test_file.write("    tree = Tree(TreeNode(tree_values[0]))\n")
    test_file.write("    for value in tree_values[1:]:\n")
    test_file.write("        tree.root.add_child(TreeNode(value))\n")
    test_file.write("    for value in tree_values:\n")
    test_file.write("        assert tree.search(tree.root, value) is not None\n")

    test_file.close()

    # Run the tests using pytest
    pytest.main(["-v", "test_main.py"])

if __name__ == "__main__":
    if not os.path.exists("test_main.py"):
        generate_tests()
    else:
        print("Test file already exists.")
