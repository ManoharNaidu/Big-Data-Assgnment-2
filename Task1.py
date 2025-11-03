'''Choosing the dataset
Puja [48664111]
Manohar [48975257]
Xavier [48655163]
[1 + 7 + 3] = 11 % 3 = 2
Thus, it is parking dataset'''

import sys
import math
import time

def read_points(path: str):
    points = []
    with open(path, "r") as file:
        for line in file:
            parts = line.split()
            if len(parts) != 3:
                continue
            id, x, y = parts
            # Convert id to int and coordinates to float
            points.append({'id': int(id), 'x': float(x), 'y': float(y)})
    return points

def euclid(ax, ay, bx, by): # distance between point 'a' and point 'b'
    return ((ax-bx)**2 + (ay - by)**2)**0.5


# Algorithm 1: Sequential Nearest Neighbor Search
''' For each query, scan every dataset point, compute distances,
    and keep the closest one.'''

def nn_seq(dataset, queries):
    start_time = time.time()
    results = []
    for query_point in queries:
        nearest_neighbor = None
        min_dist = float('inf')
        for data_point in dataset:
            distance = euclid(query_point['x'], query_point['y'], data_point['x'], data_point['y'])
            if distance < min_dist:
                min_dist = distance
                nearest_neighbor = data_point
        results.append((nearest_neighbor['id'], nearest_neighbor['x'], nearest_neighbor['y']))
    end_time = time.time()
    elapsed_time = end_time - start_time

    return results, elapsed_time

# R-Tree Node
# Node structure for the R-Tree.

B = 4 # Maximum number of entries per node
class Node(object): 
    def __init__(self):
        self.id = 0
        self.child_nodes = []
        # for leaf nodes
        self.data_points = []
        self.parent = None
        self.MBR = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }
    def perimeter(self):
        return (self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1'])

    def is_overflow(self):
        if self.is_leaf():
            if self.data_points.__len__() > B: #Checking overflows of data points, B is the upper bound.
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() > B: #Checking overflows of child nodes, B is the upper bound.
                return True
            else:
                return False

    def is_root(self):
        if self.parent is None:
            return True
        else:
            return False

    def is_leaf(self):
        if self.child_nodes.__len__() == 0:
            return True
        else:
            return False

# R-Tree
class RTree(object): #R tree class
    def __init__(self):
        self.root = Node() #Create a root
                  
    def insert(self, node, point): # insert p(data point) to u (MBR)
        if node.is_leaf(): 
            self.add_data_point(node, point) #add the data point and update the corresponding MBR
            if node.is_overflow():
                self.handle_overflow(node) #handel overflow for leaf nodes
        else:
            sub_node = self.choose_subtree(node, point) #choose a subtree to insert the data point to miminize the perimeter sum
            self.insert(sub_node, point) #keep continue to check the next layer recursively
            self.update_mbr(sub_node) #update the MBR for inserting the data point

    def add_data_point(self, node, data_point): #add data points and update the the MBRS
        node.data_points.append(data_point)
        if data_point['x'] < node.MBR['x1']:
            node.MBR['x1'] = data_point['x']
        if data_point['x'] > node.MBR['x2']:
            node.MBR['x2'] = data_point['x']
        if data_point['y'] < node.MBR['y1']:
            node.MBR['y1'] = data_point['y']
        if data_point['y'] > node.MBR['y2']:
            node.MBR['y2'] = data_point['y']

    def add_child(self, node, child):
        node.child_nodes.append(child) #add child nodes to the current parent (node) and update the MBRs. It is used in handeling overflows
        child.parent = node
        if child.MBR['x1'] < node.MBR['x1']:
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']
    # return the child whose MBR requires the minimum increase in perimeter to cover p

    # return the child whose MBR requires the minimum increase in perimeter to cover p

    def handle_overflow(self, node):
        node1, node2 = self.split(node) #u1 u2 are the two splits returned by the function "split"
        # if u is root, create a new root with s1 and s2 as its' children
        if node.is_root():
            new_root = Node()
            self.add_child(new_root, node1)
            self.add_child(new_root, node2)
            self.root = new_root
            self.update_mbr(new_root)
        # if u is not root, delete u, and set s1 and s2 as u's parent's new children
        else:
            parent = node.parent
            # copy the information of s1 into u
            parent.child_nodes.remove(node)
            self.add_child(parent, node1) #link the two splits and update the corresponding MBR
            self.add_child(parent, node2)
            if parent.is_overflow(): #check the parent node recursively
                self.handle_overflow(parent)


    def choose_subtree(self, node, point): 
        if node.is_leaf(): #find the leaf and insert the data point
            return node
        else:
            min_increase = sys.maxsize #set an initial value
            best_child = None
            for child in node.child_nodes: #check each child to find the best node to insert the point 
                if min_increase > self.peri_increase(child, point):
                    min_increase = self.peri_increase(child, point)
                    best_child = child
            return best_child

    def peri_increase(self, node, point): # calculate the increase of the perimeter after inserting the new data point
        # new perimeter - original perimeter = increase of perimeter
        origin_mbr = node.MBR
        x1, x2, y1, y2 = origin_mbr['x1'], origin_mbr['x2'], origin_mbr['y1'], origin_mbr['y2']
        increase = (max([x1, x2, point['x']]) - min([x1, x2, point['x']]) +
                    max([y1, y2, point['y']]) - min([y1, y2, point['y']])) - node.perimeter()
        return increase

            
    def split(self, node): #split a node into two nodes 
        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize
        # u is a leaf node
        if node.is_leaf():
            m = node.data_points.__len__()
            # create two different kinds of divides
            divides = [sorted(node.data_points, key=lambda data_point: data_point['x']),
                       sorted(node.data_points, key=lambda data_point: data_point['y'])] #sorting the points based on X dimension and Y dimension
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations to find a near-optimal one
                    s1 = Node()
                    s1.data_points = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.data_points = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter(): 
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        # u is a internal node
        else:
            # create four different kinds of divides
            m = node.child_nodes.__len__()
            divides = [sorted(node.child_nodes, key=lambda child_node: child_node.MBR['x1']), #sorting based on MBRs
                       sorted(node.child_nodes, key=lambda child_node: child_node.MBR['x2']),
                       sorted(node.child_nodes, key=lambda child_node: child_node.MBR['y1']),
                       sorted(node.child_nodes, key=lambda child_node: child_node.MBR['y2'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1): #check the combinations
                    s1 = Node()
                    s1.child_nodes = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_nodes = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2

        return best_s1, best_s2

        
    def update_mbr(self, node): #update MBRs when forming a new MBR. It is used in checking the combinations and update the root
        x_list = []
        y_list = []
        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else:
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
        new_mbr = {
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.MBR = new_mbr


def mindist_point_rect(x, y, mbr):
    x1, y1, x2, y2 = float(mbr['x1']), float(mbr['y1']), float(mbr['x2']), float(mbr['y2'])
    mbr_x = min(max(float(x), x1), x2)
    mbr_y = min(max(float(y), y1), y2)
    return euclid(float(x), float(y), mbr_x, mbr_y)


# Algorithm 2: Branch-and-Bound NN
def nn_bab(rtree: RTree, queries):
    t0 = time.time()
    results = []

    for query_point in queries:
        min_dist = float("inf")
        nn_point = None

        qid, qx, qy = query_point['id'], query_point['x'], query_point['y']

        root = rtree.root
        
        # Check if tree has any data
        if not root.data_points and not root.child_nodes:
            results.append((qid, None, None))
            continue

        mbr_dist = mindist_point_rect(qx, qy, root.MBR)

        H = [(root, mbr_dist, "node")]  # Priority queue of (node, bound) entries.

        while H:
            # Manually pop the entry with the smallest bound
            H.sort(key=lambda x: x[1])  # Sort by bound
            entry, distance, entry_type = H.pop(0)
            
            # If this bound is already not better than current best, skip.
            if distance >= min_dist:
                continue

            if entry_type == "leaf":
                node = entry
                # Leaf: check every point inside this node and update best if needed.
                for p in node.data_points:
                    dist = euclid(qx, qy, p['x'], p['y'])
                    if dist < min_dist or (abs(dist - min_dist) <= 1e-12 and (nn_point is None or p['id'] < nn_point['id'])):
                        min_dist = dist
                        nn_point = p
            else:
                # Internal: push promising children whose bounds are still better
                for child in entry.child_nodes:
                    bound = mindist_point_rect(qx, qy, child.MBR)
                    if bound < min_dist:
                        H.append((child, bound, "leaf" if child.is_leaf() else "node"))

        # Write out the best neighbor found for this query.
        if nn_point is None:
            results.append((qid, None, None))
        else:
            # FIX: Access dictionary keys, not indices
            results.append((nn_point['id'], nn_point['x'], nn_point['y']))

    return results, time.time() - t0


# Algorithm 3: Branch and Bound - Divide and Conquer
def split_dataset(points):
    # splitting dataset by mean of x coordinate
    x_coords = [p['x'] for p in points]
    mean_x = sum(x_coords) / len(x_coords) if x_coords else 0
    left = [p for p in points if p['x'] < mean_x]
    right = [p for p in points if p['x'] >= mean_x]
    return left, right

def nn_bab_divide(points, queries):
    
    left_points, right_points = split_dataset(points)

    # Build two separate R-Trees (left and right halves).
    left_rtree, right_rtree = RTree(), RTree()
    
    for point in left_points:
        left_rtree.insert(left_rtree.root, point)

    for point in right_points:
        right_rtree.insert(right_rtree.root, point)

    t0 = time.time()
    # Answer each query by running BaB on both trees and comparing results.
    results = []

    left_results, _ = nn_bab(left_rtree, queries)
    right_results, _ = nn_bab(right_rtree, queries)

    for i, query in enumerate(queries):
        qx, qy = query['x'], query['y']
        
        l_res = left_results[i]
        r_res = right_results[i]
        
        # Extract coordinates
        l_id, lx, ly = l_res[0], l_res[1], l_res[2]
        r_id, rx, ry = r_res[0], r_res[1], r_res[2]

        # Handle cases where one or both trees have no result
        if lx is None and rx is None:
            results.append((None, None, None))
        elif lx is None:
            results.append((r_id, rx, ry))
        elif rx is None:
            results.append((l_id, lx, ly))
        else:
            # FIX: Calculate distance from QUERY point, not origin
            l_dist = euclid(qx, qy, lx, ly)
            r_dist = euclid(qx, qy, rx, ry)
            if l_dist < r_dist:
                results.append((l_id, lx, ly))
            else:
                results.append((r_id, rx, ry))

    total_time = time.time() - t0
    return results, total_time, total_time


def save_output(path, results, total_time):
    with open(path, "w") as file:
        for result in results:
            id, x, y = result[0], result[1], result[2]
            if id is not None:
                file.write(f"{id} {x} {y}\n")
            else:
                file.write("None None None\n")
        file.write(f"\n- TOTAL_RUNNING_TIME_SECONDS = {total_time}\n")
    print(f" - Output saved to: {path}")


def main():
    data_path = "./Task1_Datasets/parking.txt"
    query_path = "./Task1_Datasets/query_points.txt"
    out_dir = "./Task1_Results"

    dataset = read_points(data_path)
    queries = read_points(query_path)

    # 1) Sequential NN
    print("Running Sequential Nearest Neighbour Search...")
    seq_results, seq_runtime = nn_seq(dataset, queries)
    save_output(f"{out_dir}/Sequential_Scan.txt", seq_results, seq_runtime)

    print("\nBuilding R-Tree...")
    rtree = RTree()
    for point in dataset:
        rtree.insert(rtree.root, point)
    
    # 2) BaB
    print("\nRunning Branch-and-Bound Nearest Neighbour Search...")
    bab_results, bab_runtime = nn_bab(rtree, queries)
    save_output(f"{out_dir}/BAB.txt", bab_results, bab_runtime)

    # 3) BaB + Divide & Conquer
    print("\nRunning Branch-and-Bound with Divide and Conquer Nearest Neighbour Search...")
    dc_results, dc_runtime, _ = nn_bab_divide(dataset, queries)
    save_output(f"{out_dir}/BAB_DC.txt", dc_results, dc_runtime)

    print("\nAll tasks completed. Output files saved in:", out_dir)

if __name__ == "__main__":
    main()