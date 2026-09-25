import json
import os

problems = {
    "hollow-diamond-pattern": {
        "title": "Hollow Diamond Pattern",
        "slug": "hollow-diamond-pattern",
        "tags": ["star-pattern"],
        "difficulty": "Medium",
        "inputFormat": "A single integer n (number of rows for the upper half).",
        "outputFormat": "The hollow diamond pattern using '*' and spaces.",
        "constraints": "2 <= n <= 100",
        "examples": [{"input": "3", "output": "  *\n * *\n*   *\n * *\n  *"}, {"input": "2", "output": " *\n* *\n *"}]
    },
    "butterfly-pattern": {
        "title": "Butterfly Pattern",
        "slug": "butterfly-pattern",
        "tags": ["star-pattern"],
        "difficulty": "Medium",
        "inputFormat": "A single integer n (number of rows for the upper half).",
        "outputFormat": "The butterfly pattern using '*' and spaces.",
        "constraints": "2 <= n <= 100",
        "examples": [{"input": "3", "output": "*    *\n**  **\n******\n**  **\n*    *"}, {"input": "2", "output": "*  *\n****\n*  *"}]
    }
}

base = "/Users/vuelancer/Downloads/zap-problem-bank/problems/"
for k, v in problems.items():
    os.makedirs(f"{base}{k}", exist_ok=True)
    with open(f"{base}{k}/problem.json", "w") as f:
        json.dump(v, f, indent=2)

print("Generated.")
