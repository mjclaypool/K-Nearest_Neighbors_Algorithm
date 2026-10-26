import os, sys, math
from functools import cmp_to_key

# This imports from a file that will be present in the
# grading system. No need to alter for local testing -
# if the file isn't present then these lines are skipped
try:
    from compile_with_soln import grader_stub
    grader = grader_stub()
except:
    pass

N = 0   # number of points
D = 0   # dimensionality of space
K = 0   # number of nearest neighbors to find for each point
# Note: K is always odd
P = []
d = 0
# true_pos = 0
# false_neg = 0
# false_pos = 0
# true_neg = 0

# ----------------------------------------
# This function (which will be compiled with our code
# when it is submitted to the grading system) takes
# the index of a point (in 0..N-1) and returns either
# +1 or -1 depending on its class.

# grader.get_class(i)
# ----------------------------------------

# ----------------------------------------
# This function (which will be compiled with our code
# when it is submitted to the grading system) takes
# the index i of a point (in 0..N-1) and the index of a
# coordinate (in 0..D-1) and returns the jth coordinate
# of the ith point.

# grader.get_coord(i, j)
# ----------------------------------------


# For testing on your own system, you can call these functions.
# They provide a simple 2D set of points, with x's being
# class +1 and o's being class -1.
#
#    o    o
# x   x
#
#    o    o
# x   x
#
# The correct confusion matrix for this instance is:
#
# Predicted: +1  -1
# Actual: +1  2   2
#         -1  3   1
#
# Don't forget to switch your code back to calling
# grader.get_class() and grader.get_coord() before
# submitting.
def get_class_local(index):
    if index < 0 or index >= 8:
        print('get_class_local: Invalid point index!')
        sys.exit(0)
    return 1 if index < 4 else -1

def get_coord_local(i, j):
    pts = [[0.0,0.0], [4.0,0.0], [4.0,3.0], [0.0,3.0],
           [3.0,1.0], [8.0,1.0], [8.0,4.0], [3.0,4.0]]
    if i < 0 or i >= 8:
        print('get_coord_local: Invalid point index!')
        sys.exit(0)
    if j < 0 or j >= 2:
        print('get_coord_local: Invalid coordinate index!')
        sys.exit(0)
    return pts[i][j]

class Node:
    def __init__(self, index):
        self.index = index
        self.size = 1
        self.left = None
        self.right = None

class Neighbor:
    def __init__(self, index, dist):
        self.index = index
        self.dist = dist

def update_size(root: Node):
    root.size = 1
    if root.left is not None:
        left_node = root.left
        root.size = root.size + left_node.size
    if root.right is not None:
        right_node = root.right
        root.size = root.size + right_node.size

def insert(root: Node, index, dim):
    if root is None:
        n = Node(index)
        return n
    if (index == root.index): #not sure if this is necessary
        return root
    if P[index][dim] < P[root.index][dim]:
        root.left = insert(root.left, index, (dim + 1)%D)
    else:
        root.right = insert(root.right, index, (dim + 1)%D)
    update_size(root)
    return root

def calculate_dist(point, root):
    m = 0
    squared_dist = 0
    while m < D:
        squared_dist = squared_dist + (abs(point[m] - root[m]))**2
        m = m + 1
    return math.sqrt(squared_dist)

def find_neighbors(root: Node, i, dim, nearest_neighbors):
    global d
    neighbor_update = False
    if root.index == i:
        if root.right is not None:
            find_neighbors(root.right, i, (dim + 1)%D, nearest_neighbors)
        if root.left is not None:
            find_neighbors(root.left, i, (dim + 1)%D, nearest_neighbors)
    else:
        b = abs(P[i][dim] - P[root.index][dim])
        if b == 0:
            direction = 1
        else:
            direction = (P[i][dim] - P[root.index][dim]) / b
        dist = calculate_dist(P[i], P[root.index])
        neighbors_length = len(nearest_neighbors)

        n = Neighbor(root.index, dist)
        n_dist = n.dist
        if neighbors_length < K:
            insert_index = 0
            m = 0
            while m < neighbors_length:
                if n_dist > nearest_neighbors[m].dist:
                    insert_index = insert_index + 1
                m = m + 1
            nearest_neighbors.insert(insert_index, n)
            neighbor_update = True
            z = 0
            while z < len(nearest_neighbors):
                z = z + 1
            d = nearest_neighbors[neighbors_length - 1].dist
        else:
            if n_dist < d:
                insert_index = 0
                m = 0
                while m < neighbors_length:
                    if n_dist > nearest_neighbors[m].dist:
                        insert_index = insert_index + 1
                    m = m + 1
                nearest_neighbors.insert(insert_index, n)
                nearest_neighbors.pop()
                neighbor_update = True
                d = nearest_neighbors[neighbors_length - 1].dist
        if neighbor_update is False:
            if direction > 0:
                if root.right is not None:
                    find_neighbors(root.right, i, (dim + 1)%D, nearest_neighbors)
            else:
                if root.left is not None:
                    find_neighbors(root.left, i, (dim + 1)%D, nearest_neighbors)
        elif d > b or neighbors_length < K:
            if direction > 0:
                if root.right is not None:
                    find_neighbors(root.right, i, (dim + 1)%D, nearest_neighbors)
                if root.left is not None:
                    find_neighbors(root.left, i, (dim + 1)%D, nearest_neighbors)
            else:
                if root.left is not None:
                    find_neighbors(root.left, i, (dim + 1)%D, nearest_neighbors)
                if root.right is not None:
                    find_neighbors(root.right, i, (dim + 1)%D, nearest_neighbors)
    return nearest_neighbors

def classify_neighbors(my_neighbors):
    m = 0
    classification = 0
    while m < len(my_neighbors):
        classification = classification + grader.get_class(my_neighbors[m].index)
        m = m + 1
    return classification

def classify_prediction(actual_class, predicted_class, true_pos, false_neg, false_pos, true_neg):
    if actual_class > 0 and predicted_class > 0:
        true_pos = true_pos + 1
    elif actual_class > 0 and predicted_class < 0:
        false_neg = false_neg + 1
    elif actual_class < 0 and predicted_class > 0:
        false_pos = false_pos + 1
    else:
        true_neg = true_neg + 1
    return true_pos, false_neg, false_pos, true_neg

def main():
    global N, D, K
    # The values for N, D, and K are set in the grading system through
    # environment variables, if present.  If not present, feel
    # welcome to set N to any value you want for local testing.
    try:
        N = int(os.environ["N"])
        D = int(os.environ["D"])
        K = int(os.environ["K"])
    except:
        N = 8
        D = 2
        K = 3
        
    # Below is the part of main() you should modify.
    # (you are welcome to write other functions above
    # and call them here, but all your code should be
    # submitted in this one file).
    # ----------------------------------------
    i = 0
    root = None
    while i < N:
        j = 0
        point = []
        while j < D:
            point.append(grader.get_coord(i, j))
            j=j+1
        P.append(point)
        root = insert(root, i, 0)
        i=i+1
    true_pos = 0
    false_neg = 0
    false_pos = 0
    true_neg = 0
    i = 0
    while i < len(P):
        global d
        d = 0
        nearest_neighbors = []
        dim = 0
        my_neighbors = find_neighbors(root, i, dim, nearest_neighbors)
        my_prediction = classify_neighbors(my_neighbors)
        my_class = grader.get_class(i)
        true_pos, false_neg, false_pos, true_neg = classify_prediction(my_class, my_prediction, true_pos, false_neg, false_pos, true_neg)
        i = i+1

    # ----------------------------------------
    # At the end, you should print out a 2 x 2 confusion
    # matrix -- just 4 integers
    print(true_pos, false_neg)
    print(false_pos, true_neg)

if __name__ == "__main__":
    main()