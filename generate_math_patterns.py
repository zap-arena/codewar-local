import json
import os

problems = {
    "pascals-triangle": {
        "title": "Pascal's Triangle",
        "slug": "pascals-triangle",
        "tags": ["math", "pattern"],
        "difficulty": "Medium",
        "inputFormat": "A single integer numRows.",
        "outputFormat": "Print the first numRows of Pascal's triangle, with each row space-separated.",
        "constraints": "1 <= numRows <= 30",
        "examples": [{"input": "5", "output": "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1"}]
    },
    "floyds-triangle": {
        "title": "Floyd's Triangle",
        "slug": "floyds-triangle",
        "tags": ["pattern"],
        "difficulty": "Easy",
        "inputFormat": "A single integer n (number of rows).",
        "outputFormat": "Print Floyd's triangle up to n rows, space-separated.",
        "constraints": "1 <= n <= 100",
        "examples": [{"input": "4", "output": "1\n2 3\n4 5 6\n7 8 9 10"}]
    },
    "number-pyramid": {
        "title": "Number Pyramid",
        "slug": "number-pyramid",
        "tags": ["pattern"],
        "difficulty": "Medium",
        "inputFormat": "A single integer n (number of rows).",
        "outputFormat": "A centered pyramid of numbers.",
        "constraints": "1 <= n <= 9",
        "examples": [{"input": "3", "output": "  1\n 1 2\n1 2 3"}]
    },
    "fibonacci-number": {
        "title": "Fibonacci Number",
        "slug": "fibonacci-number",
        "tags": ["math"],
        "difficulty": "Easy",
        "inputFormat": "A single integer n.",
        "outputFormat": "The nth Fibonacci number.",
        "constraints": "0 <= n <= 30",
        "examples": [{"input": "4", "output": "3"}]
    }
}

base = "/Users/vuelancer/Downloads/zap-problem-bank/problems/"
for k, v in problems.items():
    os.makedirs(f"{base}{k}", exist_ok=True)
    with open(f"{base}{k}/problem.json", "w") as f:
        json.dump(v, f, indent=2)

print("Generated.")
