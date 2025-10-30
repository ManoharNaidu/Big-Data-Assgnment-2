# 7 + 1 + 3 = 11%3 = 2 => Parking dataset
import time


data_points = []
with open('./Task1_Datasets/parking.txt', 'r') as file:
    for line in file:
        id, x, y = line.strip().split(' ')
        data_points.append({'id': id, 'x': float(x), 'y': float(y)})

query_points = []
with open('./Task1_Datasets/query_points.txt', 'r') as file:
    for line in file:
        id, x, y = line.strip().split(' ')
        query_points.append({'id': id, 'x': float(x), 'y': float(y)})

# Sequential Scan Based
def eucledian_distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

results = []
start_time = time.time()
for query_point in query_points:
    nearest_neighbor = None
    min_distance = float('inf')
    for data_point in data_points:
        distance = eucledian_distance(query_point['x'], query_point['y'], data_point['x'], data_point['y'])
        if distance < min_distance:
            min_distance = distance
            nearest_neighbor = data_point
    results.append((nearest_neighbor['id'], nearest_neighbor['x'], nearest_neighbor['y'], min_distance))
end_time = time.time()

total_time = end_time - start_time
average_time = total_time / 200.0

output_path = './Task1_Results/Seq_Scan.txt'

with open(output_path, 'w') as file:
    for result in results:
        file.write(f"{result[0]} {result[1]} {result[2]} {result[3]}\n")
    file.write(f"\nTotal Time: {total_time} seconds\n")
    file.write(f"Average Time per Query: {average_time} seconds\n")

print(f"Results written to {output_path}")

