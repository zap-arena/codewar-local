import json
import os

SCENARIOS = {
    "two-sum": "<strong>Scenario: E-commerce Platform</strong><br>You are building a checkout system. A user has a gift card with a specific `target` balance. Find exactly two items in their cart (`nums`) whose prices add up to the gift card value so they can spend it entirely.",
    "group-anagrams": "<strong>Scenario: Search Engine Optimization</strong><br>Users often scramble letters when searching. Group a list of search query words into clusters of anagrams so the search engine can treat them as the same query.",
    "top-k-frequent-elements": "<strong>Scenario: Social Media Trending</strong><br>You are analyzing a stream of hashtags. Given an array of hashtag IDs, find the `k` most frequently used hashtags to display on the trending page.",
    "valid-parentheses": "<strong>Scenario: Code Compiler</strong><br>You are writing a syntax checker for a new programming language. Given a string of brackets, determine if every opened bracket is correctly closed in the right order.",
    "majority-element": "<strong>Scenario: Voting System</strong><br>You are analyzing election data. Given an array of votes, find the candidate ID that holds the absolute majority.",
    "contains-duplicate-ii": "<strong>Scenario: Rate Limiting System</strong><br>To prevent spam, you must check if a user has sent the identical message ID twice within a sliding window of `k` seconds.",
    "intersection-of-two-arrays": "<strong>Scenario: Mutual Friends</strong><br>You are building a social network feature. Given the friend lists of two users, find the IDs of all mutual friends.",
    "valid-palindrome": "<strong>Scenario: DNA Sequence Validation</strong><br>A bioinformatics tool needs to check if a DNA sequence string (ignoring spaces and non-alphanumeric characters) reads the same forwards and backwards.",
    "merge-sorted-array": "<strong>Scenario: Database Shard Merging</strong><br>Two distributed database shards have returned sorted lists of user IDs. Merge them in-place into a single sorted list for the frontend.",
    "reverse-string": "<strong>Scenario: Embedded Systems Memory</strong><br>You are programming a micro-controller with extremely limited RAM. Reverse a string buffer in-place without allocating any extra memory.",
    "longest-substring-without-repeating-characters": "<strong>Scenario: Network Packet Analysis</strong><br>You are analyzing a stream of network packets. Find the length of the longest contiguous sequence of packets where no two packets have the same ID.",
    "trapping-rain-water": "<strong>Scenario: Civil Engineering</strong><br>You are designing a city's drainage system. Given an elevation map representing the heights of buildings, calculate how much rainwater can be trapped between them after a storm.",
    "move-zeroes": "<strong>Scenario: Disk Defragmentation</strong><br>A storage disk represents empty blocks as 0. Shift all valid data to the front of the disk to create one contiguous block of free space at the end.",
    "remove-element": "<strong>Scenario: Content Moderation</strong><br>A cache block contains an array of user IDs. You must filter out all users who match a flagged ID in-place to save memory.",
    "two-sum-ii": "<strong>Scenario: Ledger Reconciliation</strong><br>You have a chronologically sorted array of transaction amounts. Find two transactions that exactly offset a known discrepancy target."
}

def dump_problem(path):
    with open(f"{path}/problem.json") as f:
        problem = json.load(f)
    
    slug = problem["slug"]
    tags = problem.get("tags", [])
    
    # Inject tags for known ones if missing
    if slug in ["two-sum", "group-anagrams", "top-k-frequent-elements", "valid-parentheses", "majority-element", "contains-duplicate-ii", "intersection-of-two-arrays"]:
        if "hash-map" not in tags: tags.append("hash-map")
    if slug in ["valid-palindrome", "merge-sorted-array", "reverse-string", "longest-substring-without-repeating-characters", "trapping-rain-water", "move-zeroes", "remove-element", "two-sum-ii"]:
        if "two-pointers" not in tags: tags.append("two-pointers")
        
    is_two_pointer = "two-pointers" in tags
    opt_text = "<br><br><strong>Optimization Scenarios (Two Pointers):</strong><ul><li>Try to solve this using strictly O(1) auxiliary space (in-place).</li><li>Optimize your approach to run in a single pass (O(N) time complexity) without nested loops.</li></ul>"
    
    samples = []
    if "examples" in problem:
        for ex in problem["examples"]:
            samples.append({
                "input": ex["input"],
                "output": ex["output"]
            })
    
    base_stmt = f"<strong>Input:</strong> {problem.get('inputFormat', '')}<br><br><strong>Output:</strong> {problem.get('outputFormat', '')}<br><br><strong>Constraints:</strong> {problem.get('constraints', '')}"
    scenario = SCENARIOS.get(slug, "")
    
    stmt = f"{scenario}<br><br>{base_stmt}" if scenario else base_stmt
    if is_two_pointer:
        stmt += opt_text
        
    stages_data = [{
        "title": problem["title"],
        "complexity": problem.get("difficulty", "Medium"),
        "statement": stmt,
        "samples": samples
    }]
    
    return {
        "problem": {
            "title": problem["title"],
            "slug": slug,
            "tags": tags
        },
        "stages": stages_data
    }

# Hashmap
two_sum = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/two-sum")
group_anagrams = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/group-anagrams")
top_k = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/top-k-frequent-elements")
valid_paren = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/valid-parentheses")
majority_elem = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/majority-element")
contains_dup_ii = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/contains-duplicate-ii")
intersection = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/intersection-of-two-arrays")

# Two pointers
palindrome = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/valid-palindrome")
merge_sorted = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/merge-sorted-array")
reverse_string = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/reverse-string")
longest_sub = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/longest-substring-without-repeating-characters")
trapping_rain = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/trapping-rain-water")
move_zeroes = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/move-zeroes")
remove_elem = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/remove-element")
two_sum_ii = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/two-sum-ii")

with open("/Users/vuelancer/Downloads/codewar-offline/dump.json", "w") as f:
    json.dump([two_sum, group_anagrams, top_k, valid_paren, majority_elem, contains_dup_ii, intersection, palindrome, merge_sorted, reverse_string, longest_sub, trapping_rain, move_zeroes, remove_elem, two_sum_ii], f, indent=2)
