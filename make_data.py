import json

with open("dump.json") as f:
    dumped = json.load(f)

# The boilerplate string from data.js
boilerplate = """// Shared boilerplates for different languages
const BOILERPLATE = {
  python: `import sys\\n\\ndef solve():\\n    # Read all input from standard input\\n    input_data = sys.stdin.read().split()\\n    if not input_data:\\n        return\\n    \\n    # TODO: Implement your solution here\\n    pass\\n\\nif __name__ == '__main__':\\n    solve()\\n`,
  javascript: `const fs = require('fs');\\n\\nfunction solve() {\\n    const input = fs.readFileSync(0, 'utf-8').trim().split(/\\\\s+/);\\n    if (input.length === 0 || input[0] === '') return;\\n    \\n    // TODO: Implement your solution here\\n}\\n\\nsolve();\\n`,
  cpp: `#include <iostream>\\n#include <vector>\\n\\nusing namespace std;\\n\\nint main() {\\n    // Fast I/O\\n    ios_base::sync_with_stdio(false);\\n    cin.tie(NULL);\\n    \\n    // TODO: Implement your solution here\\n    \\n    return 0;\\n}\\n`,
  java: `import java.util.*;\\n\\npublic class Main {\\n    public static void main(String[] args) {\\n        Scanner scanner = new Scanner(System.in);\\n        if (!scanner.hasNext()) return;\\n        \\n        // TODO: Implement your solution here\\n    }\\n}\\n`,
  c: `#include <stdio.h>\\n#include <stdlib.h>\\n\\nint main() {\\n    // TODO: Implement your solution here\\n    return 0;\\n}\\n`
};

"""

# Contains duplicate data converted to `samples`
contains_duplicate = {
    "problem": {
      "title": "Contains Duplicate",
      "slug": "contains-duplicate-progressive",
    },
    "stages": [
      {
        "title": "Stage 1 \u2014 Contains Duplicate",
        "complexity": "O(n)",
        "statement": "Given an array of <code>n</code> integers, print <code>1</code> if any value appears at least twice in the array, otherwise print <code>0</code>.<br><br>This is the warm-up stage of the chain \u2014 a plain existence check.",
        "samples": [
          {
            "input": "5\n1 2 3 4 5",
            "output": "0"
          }
        ]
      },
      {
        "title": "Stage 2 \u2014 Find the Duplicate Index",
        "complexity": "O(n)",
        "statement": "Enhancement of Stage 1: instead of just saying whether a duplicate exists, print the <strong>0-based index</strong> of the first element that duplicates a value seen earlier in the array. If no duplicate exists, print <code>-1</code>.<br><br>Your solution must run in <strong>O(n)</strong> time using a hash set/map \u2014 an O(n^2) brute-force comparison of every pair will time out once <code>n</code> grows large.",
        "samples": [
          {
            "input": "5\n1 2 3 2 5",
            "output": "3"
          }
        ]
      },
      {
        "title": "Stage 3 \u2014 Count Distinct Duplicated Values",
        "complexity": "O(n)",
        "statement": "Enhancement of Stage 2: print how many <strong>distinct values</strong> appear two or more times in the array (not the total count of repeated elements \u2014 count each duplicated value once).<br><br>Still solvable in <strong>O(n)</strong> with a frequency map.",
        "samples": [
          {
            "input": "6\n1 2 2 3 3 4",
            "output": "2"
          }
        ]
      },
      {
        "title": "Stage 4 \u2014 Most Frequent Value",
        "complexity": "O(n)",
        "statement": "Enhancement of Stage 3: print the value that occurs <strong>most often</strong> in the array. If several values tie for the highest frequency, print the <strong>smallest</strong> such value.<br><br>Still <strong>O(n)</strong>: one pass to build a frequency map, one pass to find the best value.",
        "samples": [
          {
            "input": "6\n1 2 2 3 3 4",
            "output": "2"
          }
        ]
      }
    ]
}

problems = dumped + [contains_duplicate]

with open("data.js", "w") as f:
    f.write(boilerplate)
    f.write("const PROBLEMS = ")
    f.write(json.dumps(problems, indent=2))
    f.write(";\n")
