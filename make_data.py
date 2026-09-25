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

problems = dumped

with open("data.js", "w") as f:
    f.write(boilerplate)
    f.write("const PROBLEMS = ")
    f.write(json.dumps(problems, indent=2))
    f.write(";\n")
