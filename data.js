// Stage data + language boilerplates for the Contains Duplicate Code War chain.
// Sourced from problems/contains-duplicate-progressive/problem.json + boilerplate/*.

const PROBLEM = {
  title: "Contains Duplicate (Code War Chain)",
  slug: "contains-duplicate-progressive",
};

const STAGES = [
  {
    title: "Stage 1 — Contains Duplicate",
    complexity: "O(n)",
    statement:
      "Given an array of <code>n</code> integers, print <code>1</code> if any value appears at least twice in the array, otherwise print <code>0</code>.<br><br>This is the warm-up stage of the chain — a plain existence check.",
    input: "5\n1 2 3 4 5",
    output: "0",
  },
  {
    title: "Stage 2 — Find the Duplicate Index",
    complexity: "O(n)",
    statement:
      "Enhancement of Stage 1: instead of just saying whether a duplicate exists, print the <strong>0-based index</strong> of the first element that duplicates a value seen earlier in the array. If no duplicate exists, print <code>-1</code>.<br><br>Your solution must run in <strong>O(n)</strong> time using a hash set/map — an O(n^2) brute-force comparison of every pair will time out once <code>n</code> grows large.",
    input: "5\n1 2 3 2 5",
    output: "3",
  },
  {
    title: "Stage 3 — Count Distinct Duplicated Values",
    complexity: "O(n)",
    statement:
      "Enhancement of Stage 2: print how many <strong>distinct values</strong> appear two or more times in the array (not the total count of repeated elements — count each duplicated value once).<br><br>Still solvable in <strong>O(n)</strong> with a frequency map.",
    input: "6\n1 2 2 3 3 4",
    output: "2",
  },
  {
    title: "Stage 4 — Most Frequent Value",
    complexity: "O(n)",
    statement:
      "Enhancement of Stage 3: print the value that occurs <strong>most often</strong> in the array. If several values tie for the highest frequency, print the <strong>smallest</strong> such value.<br><br>Still <strong>O(n)</strong>: one pass to build a frequency map, one pass to find the best value.",
    input: "5\n1 3 3 3 2",
    output: "3",
  },
  {
    title: "Stage 5 — List All Duplicate Values",
    complexity: "O(n log n)",
    statement:
      "Enhancement of Stage 4: print <strong>every distinct value</strong> that appears two or more times, sorted in ascending order, space-separated on one line. If there are none, print an empty line.<br><br>Building the frequency map is still O(n), but sorting the result pushes the expected complexity to <strong>O(n log n)</strong>.",
    input: "5\n3 1 3 2 1",
    output: "1 3",
  },
  {
    title: "Stage 6 — Duplicate Within a Window of 3",
    complexity: "O(n)",
    statement:
      "Enhancement of Stage 1: print <code>1</code> if there exist two <strong>equal</strong> values whose indices are at most <strong>3 apart</strong> (<code>|i - j| &lt;= 3</code>), otherwise print <code>0</code>.<br><br>A sliding window of the last 3 values (a small hash set you add to / evict from as you scan) keeps this at <strong>O(n)</strong> — checking every pair within range for every index is O(n) per index and O(n^2) overall.",
    input: "5\n1 2 3 1 5",
    output: "1",
  },
  {
    title: "Stage 7 — Longest Subarray Without Duplicates",
    complexity: "O(n)",
    statement:
      "Final enhancement: print the length of the <strong>longest contiguous subarray</strong> that contains no duplicate values.<br><br>This is the hardest stage of the chain. A brute-force check of every subarray is O(n^2)/O(n^3). The optimal solution uses a <strong>sliding window</strong> with a hash map of last-seen indices to stay at <strong>O(n)</strong>.",
    input: "6\n1 2 3 2 4 5",
    output: "4",
  },
];

const BOILERPLATE = {
  python: `import sys


def solve(nums):
    # TODO: implement the logic described in the current stage's statement
    return 0


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:1 + n]]
    print(solve(nums))


if __name__ == "__main__":
    main()
`,
  cpp: `#include <bits/stdc++.h>
using namespace std;

long long solve(vector<long long>& nums) {
    // TODO: implement the logic described in the current stage's statement
    return 0;
}

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<long long> nums(n);
    for (auto &x : nums) cin >> x;
    cout << solve(nums) << endl;
    return 0;
}
`,
  java: `import java.util.*;

public class Main {
    static long solve(long[] nums) {
        // TODO: implement the logic described in the current stage's statement
        return 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[] nums = new long[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextLong();
        System.out.println(solve(nums));
    }
}
`,
  c: `#include <stdio.h>
#include <stdlib.h>

long solve(long *nums, int n) {
    // TODO: implement the logic described in the current stage's statement
    return 0;
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    long *nums = malloc(sizeof(long) * n);
    for (int i = 0; i < n; i++) scanf("%ld", &nums[i]);
    printf("%ld\\n", solve(nums, n));
    free(nums);
    return 0;
}
`,
};
