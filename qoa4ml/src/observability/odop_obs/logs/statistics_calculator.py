import os
import numpy as np
from scipy.stats import scoreatpercentile
from tabulate import tabulate


def process_file(file_path):
    with open(file_path, "r") as file:
        numbers = [float(line.strip()) for line in file]
        avg = np.mean(numbers)
        p99 = scoreatpercentile(numbers, 99)
        min_val = min(numbers)
        max_val = max(numbers)
    return [file_path, avg, p99, min_val, max_val]


def main(directory):
    table = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            table.append(process_file(file_path))
    headers = ["File", "Average", "P99", "Min", "Max"]
    print(tabulate(table, headers=headers, tablefmt="grid"))
    with open("result.txt", "w") as f:
        f.write(tabulate(table, headers=headers, tablefmt="grid"))


if __name__ == "__main__":
    directory = "./"
    main(directory)
