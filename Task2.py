
'''Choosing the dataset
Puja [48664111]
Manohar [48975257]
Xavier [48655163]
[1 + 7 + 3] = 11 % 3 = 2
Thus, it is city3 dataset'''

import sys
import time
import math

# Load data points
data_points = []
with open('./Task2_Datasets/city3.txt', 'r') as file:
    for line in file:
        id, x, y = line.strip().split(' ')
        data_points.append({'id': id, 'x': float(x), 'y': float(y)})

def write_results(method_name, results, total_time):

    print(f"- {method_name} Total Time: {total_time} seconds")

    output_path = "./Task2_Results/" + method_name + ".txt"
    with open(output_path, 'w') as file:
        for result in results:
            file.write(f"{result['id']} {result['x']} {result['y']}\n")
        file.write(f"\nTotal Time: {total_time} seconds\n")
    
    print(f"- {method_name} results written to {output_path}")

def dominates(p1, p2): # Check if p1 dominates p2
    return (p1["x"] <= p2["x"] and p1["y"] <= p2["y"]) and (p1["x"] < p2["x"] or p1["y"] < p2["y"])

# === Sequential Scan Based Method ===
def sequential_scan(data):
    start_time = time.time()
    skyline_result = []

    for point in data:
        dominated = False
        for other_point in data:
            if other_point["id"] != point["id"]:
                if dominates(other_point, point): # Check if other_point dominates point
                    dominated = True
                    break
        if not dominated: # if not, add point to skyline result
            skyline_result.append(point)

    end_time = time.time()
    total_time = end_time - start_time

    sorted_results = sorted(skyline_result, key=lambda p: p['id'])

    return sorted_results, total_time

print("\n\tRunning Sequential Scan Based Method...\n")
skyline_results, sequential_total_time = sequential_scan(data_points)
write_results("Sequential_Scan", skyline_results, sequential_total_time)

# === R-Tree ===
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
            return len(self.data_points) > B
        else:
            return len(self.child_nodes) > B
    
    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.child_nodes) == 0

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
        if node.MBR['x1'] == -1:  # Initialize MBR
            node.MBR = {'x1': point['x'], 'y1': point['y'], 'x2': point['x'], 'y2': point['y']}
        else:
            node.MBR['x1'] = min(node.MBR['x1'], point['x'])
            node.MBR['x2'] = max(node.MBR['x2'], point['x'])
            node.MBR['y1'] = min(node.MBR['y1'], point['y'])
            node.MBR['y2'] = max(node.MBR['y2'], point['y'])

    def add_child_node(self, node, child):
        node.child_nodes.append(child)
        child.parent = node
        self.update_mbr(node)

    def handle_overflow(self, node):
        node1, node2 = self.split(node)
        if node.is_root():
            new_root = Node()
            self.add_child_node(new_root, node1)
            self.add_child_node(new_root, node2)
            self.root = new_root
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
                increase = self.perimeter_increase(child, point)
                if increase < min_increase:
                    min_increase = increase
                    best_child = child
            return best_child
        
    def perimeter_increase(self, node, point):
        x1, y1, x2, y2 = node.MBR['x1'], node.MBR['y1'], node.MBR['x2'], node.MBR['y2']
        new_x1, new_x2 = min(x1, point['x']), max(x2, point['x'])
        new_y1, new_y2 = min(y1, point['y']), max(y2, point['y'])
        new_perimeter = 2 * ((new_x2 - new_x1) + (new_y2 - new_y1))
        return new_perimeter - node.perimeter()
    
    def split(self, node):
        best_s1, best_s2 = Node(), Node()
        best_perimeter = sys.maxsize

        if node.is_leaf():
            m = len(node.data_points)
            divides = [
                sorted(node.data_points, key=lambda p: p['x']),
                sorted(node.data_points, key=lambda p: p['y'])
            ]
            for divide in divides:
                for i in range(math.ceil(0.4*B), m - math.ceil(0.4*B) + 1):
                    s1, s2 = Node(), Node()
                    s1.data_points, s2.data_points = divide[:i], divide[i:]
                    self.update_mbr(s1), self.update_mbr(s2)
                    if s1.perimeter() + s2.perimeter() < best_perimeter:
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1, best_s2 = s1, s2
        else:
            m = len(node.child_nodes)
            divides = [
                sorted(node.child_nodes, key=lambda n: n.MBR['x1']),
                sorted(node.child_nodes, key=lambda n: n.MBR['y1']),
                sorted(node.child_nodes, key=lambda n: n.MBR['x2']),
                sorted(node.child_nodes, key=lambda n: n.MBR['y2'])
            ]
            for divide in divides:
                for i in range(math.ceil(0.4*B), m - math.ceil(0.4*B) + 1):
                    s1, s2 = Node(), Node()
                    s1.child_nodes, s2.child_nodes = divide[:i], divide[i:]
                    self.update_mbr(s1), self.update_mbr(s2)
                    if s1.perimeter() + s2.perimeter() < best_perimeter:
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1, best_s2 = s1, s2
        
        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2
            
        return best_s1, best_s2
    
    def update_mbr(self, node):
        if node.is_leaf():
            if not node.data_points:
                return
            x_coords = [p['x'] for p in node.data_points]
            y_coords = [p['y'] for p in node.data_points]
            node.MBR = {
                'x1': min(x_coords), 'x2': max(x_coords),
                'y1': min(y_coords), 'y2': max(y_coords)
            }
        else:
            if not node.child_nodes:
                return
            x_coords = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_coords = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
            node.MBR = {
                'x1': min(x_coords), 'x2': max(x_coords),
                'y1': min(y_coords), 'y2': max(y_coords)
            }

# Build R-Tree
print("\n\t\t*** Building R-Tree ***\n")
rtree = RTree()
for point in data_points:
    rtree.insert(rtree.root, point)

print("The MBR of the root is:", rtree.root.MBR)

def mindist_to_origin(mbr): # calculating distance from origin to MBR's lower-left corner
    return math.sqrt(mbr['x1']**2 + mbr['y1']**2)

# === Branch and Bound Skyline Algorithm (BBS) ===
def BBS(rtree):
    SKY = [] 
    H = []  
    
    # Step 1: Insert root MBR into H
    root_dist = mindist_to_origin(rtree.root.MBR)
    H.append((rtree.root, root_dist, 'node'))

    while H:
        H.sort(key=lambda x: x[1])
        entry, distance, entry_type = H.pop(0) 
        if entry_type == 'node': # check if entry is node 
            node = entry
            
            dominated = False 
            ll_corner = {'x': node.MBR['x1'], 'y': node.MBR['y1']}
            for sky_point in SKY:
                if dominates(sky_point, ll_corner): # Check if any skyline point dominates the lower-left corner of this MBR
                    dominated = True
                    break
            
            if not dominated: # if not dominated, insert all the child entries into H
                if node.is_leaf(): # if the node is leaf, insert all data points along with their distances
                    for point in node.data_points: 
                        point_dist = math.sqrt(point['x']**2 + point['y']**2)
                        H.append((point, point_dist, 'point'))
                else: 
                    for child in node.child_nodes: # if not leaf node, Insert all child nodes along with their distances
                        child_dist = mindist_to_origin(child.MBR)
                        H.append((child, child_dist, 'node'))
        
        else: # entry is a data point
            point = entry
            
            dominated = False
            for sky_point in SKY: # Check if any skyline point dominates this point
                if dominates(sky_point, point):
                    dominated = True
                    break

            if not dominated: # If not dominated, insert to skyline
                SKY.append(point)
    
    return SKY

print("\n\tRunning Branch and Bound Skyline Algorithm (BBS)...\n")
start_time = time.time()
bbs_results = BBS(rtree)
end_time = time.time()

bbs_total_time = end_time - start_time
sorted_bbs_results = sorted(bbs_results, key=lambda p: p['id'])
write_results("BBS", sorted_bbs_results, bbs_total_time)

# === BBS with Divide and Conquer ===
def BBS_DC():

    # Divide data points into left and right subsets based on mean x-coordinate
    x_values = [point["x"] for point in data_points]
    mean_x = sum(x_values) / len(x_values)

    left_points = [point for point in data_points if point["x"] <= mean_x]
    right_points = [point for point in data_points if point["x"] > mean_x]

    # Build R-Trees for both subsets

    print("\n\t*** Building R-Tree for Left Subset ***\n")
    left_rtree = RTree()
    for point in left_points:
        left_rtree.insert(left_rtree.root, point)

    print("The MBR of the left R-Tree root is:", left_rtree.root.MBR)

    print("\n\t*** Building R-Tree for Right Subset ***\n")
    right_rtree = RTree()
    for point in right_points:
        right_rtree.insert(right_rtree.root, point)
    
    print("The MBR of the right R-Tree root is:", right_rtree.root.MBR, "\n")
    
    start_time = time.time()

    # Get skyline results from both subsets using BBS
    left_skyline = BBS(left_rtree)
    right_skyline = BBS(right_rtree)

    final_skyline = left_skyline

    for point in right_skyline:
        dominated = False
        for sky_point in final_skyline:
            if dominates(sky_point, point):
                dominated = True
                break
        if not dominated:
            final_skyline.append(point)
    end_time = time.time()
    total_time = end_time - start_time

    sorted_results = sorted(final_skyline, key=lambda p: p['id'])
    
    return sorted_results, total_time

print("\n\tRunning BBS with Divide and Conquer...\n")
bbs_dc_results, bbs_dc_total_time = BBS_DC()
write_results("BBS_DC", bbs_dc_results, bbs_dc_total_time)
