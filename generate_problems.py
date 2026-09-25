import json
import os

problems = {
    "majority-element": {
        "title": "Majority Element",
        "slug": "majority-element",
        "tags": ["hash-map"],
        "difficulty": "Easy",
        "inputFormat": "Line 1: integer n.\nLine 2: n space-separated integers.",
        "outputFormat": "A single integer: the majority element.",
        "constraints": "1 <= n <= 5 * 10^4\n-10^9 <= nums[i] <= 10^9",
        "examples": [{"input": "3\n3 2 3", "output": "3"}, {"input": "7\n2 2 1 1 1 2 2", "output": "2"}]
    },
    "contains-duplicate-ii": {
        "title": "Contains Duplicate II",
        "slug": "contains-duplicate-ii",
        "tags": ["hash-map"],
        "difficulty": "Easy",
        "inputFormat": "Line 1: integers n and k.\nLine 2: n space-separated integers.",
        "outputFormat": "true or false",
        "constraints": "1 <= n <= 10^5\n0 <= k <= 10^5",
        "examples": [{"input": "4 3\n1 2 3 1", "output": "true"}, {"input": "6 2\n1 2 3 1 2 3", "output": "false"}]
    },
    "intersection-of-two-arrays": {
        "title": "Intersection of Two Arrays",
        "slug": "intersection-of-two-arrays",
        "tags": ["hash-map"],
        "difficulty": "Easy",
        "inputFormat": "Line 1: integer n.\nLine 2: n space-separated integers.\nLine 3: integer m.\nLine 4: m space-separated integers.",
        "outputFormat": "Space-separated unique integers present in both arrays.",
        "constraints": "1 <= n, m <= 1000",
        "examples": [{"input": "4\n1 2 2 1\n2\n2 2", "output": "2"}, {"input": "3\n4 9 5\n5\n9 4 9 8 4", "output": "4 9"}]
    },
    "move-zeroes": {
        "title": "Move Zeroes",
        "slug": "move-zeroes",
        "tags": ["two-pointers"],
        "difficulty": "Easy",
        "inputFormat": "Line 1: integer n.\nLine 2: n space-separated integers.",
        "outputFormat": "n space-separated integers with zeroes at the end.",
        "constraints": "1 <= n <= 10^4",
        "examples": [{"input": "5\n0 1 0 3 12", "output": "1 3 12 0 0"}, {"input": "1\n0", "output": "0"}]
    },
    "remove-element": {
        "title": "Remove Element",
        "slug": "remove-element",
        "tags": ["two-pointers"],
        "difficulty": "Easy",
        "inputFormat": "Line 1: integer n and val.\nLine 2: n space-separated integers.",
        "outputFormat": "Space-separated integers remaining after removing val.",
        "constraints": "0 <= n <= 100\n0 <= val <= 100",
        "examples": [{"input": "4 3\n3 2 2 3", "output": "2 2"}, {"input": "5 2\n0 1 2 2 3", "output": "0 1 3"}]
    },
    "two-sum-ii": {
        "title": "Two Sum II",
        "slug": "two-sum-ii",
        "tags": ["two-pointers"],
        "difficulty": "Medium",
        "inputFormat": "Line 1: integer n.\nLine 2: n space-separated integers sorted ascending.\nLine 3: integer target.",
        "outputFormat": "Two space-separated 1-indexed positions.",
        "constraints": "2 <= n <= 3 * 10^4",
        "examples": [{"input": "4\n2 7 11 15\n9", "output": "1 2"}, {"input": "3\n2 3 4\n6", "output": "1 3"}]
    }
}

base = "/Users/vuelancer/Downloads/zap-problem-bank/problems/"
for k, v in problems.items():
    with open(f"{base}{k}/problem.json", "w") as f:
        json.dump(v, f, indent=2)

print("Generated.")
