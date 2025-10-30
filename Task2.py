# 7 + 1 + 3 = 11%3 = 2 => city3 dataset
import sys
import time
import math

data_points = []

with open('./Task2_Datasets/city3.txt', 'r') as file:
    for line in file:
        id, x, y = line.strip().split(' ') # read each line and split into id, x, y
        data_points.append({'id': id, 'x': float(x), 'y': float(y)})

def dominates(p1, p2): # check if p1 dominates p2
    return (p1["x"] >= p2["x"] and p1["y"] > p2["y"]) or (p1["x"] > p2["x"] and p1["y"] >= p2["y"])

# === Sequential Scan Based Method ===
def sequential_scan(data):
    start_time = time.time()
    skyline_result = []

    for point in data:
        dominated_by_other = False
        for other_point in data:
            if other_point["id"] != point["id"]: # if two points are not same only then we check if one point dominates other
                if dominates(point, other_point):
                    dominated_by_other = True # 'other_point' dominates 'point'
                    break
        if not dominated_by_other: # if 'point' is not dominated by any other point, add to skyline result
            skyline_result.append(point)

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / len(data)

    print(f"Total Time: {total_time} seconds")
    print(f"Average Time per Point: {average_time} seconds")
    
    output_path = './Task2_Results/Seq_Scan.txt'
    with open(output_path, 'w') as file:
        for result in skyline_result:
            file.write(f"{result['id']} {result['x']} {result['y']}\n")
        file.write(f"\nTotal Time: {total_time} seconds\n")
        file.write(f"Average Time per Point: {average_time} seconds\n")

    print(f"Results written to {output_path}\n")

print("Running Sequential Scan Based Method...\n")
sequential_scan(data_points)

# === Branch and Bound Skyline Algorithm (BBS) ===

B = 4

class Node:
    def __init__(self):
        self.id = 0
        self.child_nodes = []
        self.data_points = []
        self.parent = None
        self.MBR = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1
        }

    def perimeter(self):
        return 2 * ((self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1']))
    
    def is_overflow(self):
        if self.is_leaf():
            if self.data_points.__len__() > B: # checking overflow condition for data points for leaf node
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() > B: # checking overflow condition for child nodes for non-leaf node
                return True
            else:
                return False
    
    def is_root(self):
        if self.parent is None:
            return True
        return False

    def is_leaf(self):
        if self.child_nodes.__len__() == 0:
            return True
        return False
 
class RTree:
    def __init__(self):
        self.root = Node()

    def insert(self, node, point):
        if node.is_leaf():
            self.add_data_point(node, point)

            if node.is_overflow():
                self.handle_overflow(node)
        else:
            sub_node = self.choose_subtree(node, point)
            self.insert(sub_node, point)
            self.update_mbr(sub_node)

    def add_data_point(self, node, point):
        node.data_points.append(point)
        
        if point['x'] < node.MBR['x1']:
            node.MBR['x1'] = point['x']
        if point['x'] > node.MBR['x2']:
            node.MBR['x2'] = point['x']
        if point['y'] < node.MBR['y1']:
            node.MBR['y1'] = point['y']
        if point['y'] > node.MBR['y2']:
            node.MBR['y2'] = point['y']

    def add_child_node(self, node, child):
        node.child_nodes.append(child)
        child.parent = node
        
        if child.MBR['x1'] < node.MBR['x1']:
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']

    def handle_overflow(self, node):
        node1, node2 = self.split(node)

        if node.is_root():
            new_root = Node()
            self.add_child_node(new_root, node1)
            self.add_child_node(new_root, node2)
            self.root = new_root
            self.update_mbr(new_root)
        else:
            parent = node.parent
            parent.child_nodes.remove(node)
            self.add_child_node(parent, node1)
            self.add_child_node(parent, node2)

            if parent.is_overflow():
                self.handle_overflow(parent)
    
    def choose_subtree(self, node, point):
        if node.is_leaf():
            return node
        else:
            min_increase = sys.maxsize
            best_child = None

            for child in node.child_nodes:
                if min_increase > self.perimeter_increase(child, point):
                    min_increase = self.perimeter_increase(child, point)
                    best_child = child
            return best_child
        
    def perimeter_increase(self, node, point):

        origin_mbr = node.MBR

        x1, y1, x2, y2 = origin_mbr['x1'], origin_mbr['y1'], origin_mbr['x2'], origin_mbr['y2']

        increase = (max(x1, x2, point['x']) - min(x1, x2, point['x']) +
                    max(y1, y2, point['y']) - min(y1, y2, point['y'])) - node.perimeter()
        return increase
    
    def split(self, node):
        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize

        # if u is a lead node
        if node.is_leaf():
            m = node.data_points.__len__()

            # create two different kinds of divides
            divides = [sorted(node.data_points, key=lambda p: p['x']),
                       sorted(node.data_points, key=lambda p: p['y'])]
            
            for divide in divides:
                for i in range(math.ceil(0.4*B), m - math.ceil(0.4*B) + 1):
                    s1 = Node()
                    s1.data_points = divide[0:i]
                    self.update_mbr(s1)

                    s2 = Node()
                    s2.data_points = divide[i:divide.__len__()]
                    self.update_mbr(s2)

                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2
        # if u is a non-leaf node
        else:
            # create four different kinds of divides
            m = node.child_nodes.__len__()
            divides = [sorted(node.child_nodes, key=lambda n: n.MBR['x1']),
                       sorted(node.child_nodes, key=lambda n: n.MBR['y1']),
                       sorted(node.child_nodes, key=lambda n: n.MBR['x2']),
                       sorted(node.child_nodes, key=lambda n: n.MBR['y2'])]
            
            for divide in divides:
                for i in range(math.ceil(0.4*B), m - math.ceil(0.4*B) + 1):
                    s1 = Node()
                    s1.child_nodes = divide[0:i]
                    self.update_mbr(s1)

                    s2 = Node()
                    s2.child_nodes = divide[i:divide.__len__()]
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
    
    def update_mbr(self, node):
        x_list = []
        y_list = []

        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else:
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
            
        new_mbr = {
            "x1": min(x_list),
            "x2": max(x_list),
            "y1": min(y_list),
            "y2": max(y_list)
        }
        node.MBR = new_mbr

print("Building R-Tree...\n")
# build R-Tree and insert data points 
rtree = RTree()
for point in data_points:
    rtree.insert(rtree.root, point)

print("The MBR of the root is:", rtree.root.MBR)

def mindist_to_origin(mbr):
    return math.sqrt(mbr['x1']**2 + mbr['y1']**2)

def BBS(root):

    start_time = time.time()
    skyline_result = []

    H = []

    root_mindist = mindist_to_origin(root.MBR)
    H.append((root, root_mindist))

    while H:
        H.sort(key=lambda x: x[1]) # sort H based on mindist
        node, _ = H.pop(0) # pop the node with smallest mindist

        if node.is_leaf():
            for point in node.data_points:
                dominated = False
                for sky_point in skyline_result:
                    if dominates(sky_point, point):
                        dominated = True
                        break
                if not dominated:
                    skyline_result.append(point)
        else:
            for child in node.child_nodes:
                dominated = False
                for sky_point in skyline_result:
                    lower_left_mbr = {'x': child.MBR['x1'], 'y': child.MBR['y1']}
                    if dominates(sky_point, lower_left_mbr):
                        dominated = True
                        break
                if not dominated:
                    child_mindist = mindist_to_origin(child.MBR)
                    H.append((child, child_mindist))

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / len(data_points)

    print(f"Total Time: {total_time} seconds")
    print(f"Average Time per Point: {average_time} seconds")

    output_path = './Task2_Results/BBS.txt'
    with open(output_path, 'w') as file:
        for result in skyline_result:
            file.write(f"{result['id']} {result['x']} {result['y']}\n")
        file.write(f"\nTotal Time: {total_time} seconds\n")
        file.write(f"Average Time per Point: {average_time} seconds\n")

    print(f"BBS results written to {output_path}")

print("\nRunning Branch and Bound Skyline Algorithm (BBS)...\n")
BBS(rtree.root)
