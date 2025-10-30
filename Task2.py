
# 7 + 1 + 3 = 11%3 = 2 => city3 dataset
import sys
import time
import math

# Load data points
data_points = []
with open('./Task2_Datasets/city3.txt', 'r') as file:
    for line in file:
        id, x, y = line.strip().split(' ')
        data_points.append({'id': id, 'x': float(x), 'y': float(y)})

def dominates(p1, p2):
    # Check if p1 dominates p2 (p1 is better in all dimensions)
    return (p1["x"] <= p2["x"] and p1["y"] <= p2["y"]) and (p1["x"] < p2["x"] or p1["y"] < p2["y"])

# === Sequential Scan Based Method ===
def sequential_scan(data):
    start_time = time.time()
    skyline_result = []

    for point in data:
        dominated = False
        for other_point in data:
            if other_point["id"] != point["id"]:
                if dominates(other_point, point):
                    dominated = True
                    break
        if not dominated:
            skyline_result.append(point)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"- Sequential Scan Total Time: {total_time} seconds")

    sorted_results = sorted(skyline_result, key=lambda p: p['id'])
    skyline_result = sorted_results
    
    output_path = './Task2_Results/Seq_Scan.txt'
    with open(output_path, 'w') as file:
        for result in skyline_result:
            file.write(f"{result['id']} {result['x']} {result['y']}\n")
        file.write(f"\nTotal Time: {total_time} seconds\n")

    print(f"- Results written to {output_path}\n")
    return skyline_result

print("\n\tRunning Sequential Scan Based Method...\n")
sequential_results = sequential_scan(data_points)

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
print("\t*** Building R-Tree ***\n")
rtree = RTree()
for point in data_points:
    rtree.insert(rtree.root, point)

print("The MBR of the root is:", rtree.root.MBR)

def mindist_to_origin(mbr): # calculating distance from MBR to origin (0,0)
    return math.sqrt(mbr['x1']**2 + mbr['y1']**2)

def BBS():
    start_time = time.time()
    SKY = []  # skyline result
    H = []    # sorted list of entries (both nodes and points)
    
    # Step 1: Insert root MBR into H
    root_dist = mindist_to_origin(rtree.root.MBR)
    H.append((rtree.root, root_dist, 'node'))
    
    while H:
        H.sort(key=lambda x: x[1])
        entry, dist, entry_type = H.pop(0) # Remove first entry from H (sorted by mindist)
        if entry_type == 'node':
            node = entry
            
            dominated = False # Check if any skyline point dominates the lower-left corner of this MBR
            ll_corner = {'x': node.MBR['x1'], 'y': node.MBR['y1']}
            for sky_point in SKY:
                if dominates(sky_point, ll_corner):
                    dominated = True
                    break
            
            if not dominated: # if not dominated, insert all the child entries into H
                if node.is_leaf():
                    for point in node.data_points: # if the node is leaf, insert all data points
                        point_dist = math.sqrt(point['x']**2 + point['y']**2)
                        H.append((point, point_dist, 'point'))
                else: 
                    for child in node.child_nodes: # if not leaf node, Insert all child nodes
                        child_dist = mindist_to_origin(child.MBR)
                        H.append((child, child_dist, 'node'))
        
        else:
            point = entry
            
            dominated = False
            for sky_point in SKY: # Check if any skyline point dominates this point
                if dominates(sky_point, point):
                    dominated = True
                    break

            if not dominated: # If not dominated, insert to skyline
                SKY.append(point)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"- BBS Total Time: {total_time} seconds")

    sorted_results = sorted(SKY, key=lambda p: p['id'])
    SKY = sorted_results
    
    output_path = './Task2_Results/BBS.txt'
    with open(output_path, 'w') as file:
        for result in SKY:
            file.write(f"{result['id']} {result['x']} {result['y']}\n")
        file.write(f"\nTotal Time: {total_time} seconds\n")
    
    print(f"- BBS results written to {output_path}")
    return SKY

print("\n\tRunning Branch and Bound Skyline Algorithm (BBS)...\n")
bbs_results = BBS()