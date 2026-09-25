import json
import os

SCENARIOS = {
    "two-sum": "<strong>Scenario: E-commerce Platform</strong><br>You are building a checkout system. A user has a gift card with a specific `target` balance. Find exactly two items in their cart (`nums`) whose prices add up to the gift card value so they can spend it entirely.",
    "group-anagrams": "<strong>Scenario: Search Engine Optimization</strong><br>Users often scramble letters when searching. Group a list of search query words into clusters of anagrams so the search engine can treat them as the same query.",
    "top-k-frequent-elements": "<strong>Scenario: Social Media Trending</strong><br>You are analyzing a stream of hashtags. Given an array of hashtag IDs, find the `k` most frequently used hashtags to display on the trending page.",
    "valid-parentheses": "<strong>Scenario: Code Compiler</strong><br>You are writing a syntax checker for a new programming language. Given a string of brackets, determine if every opened bracket is correctly closed in the right order.",
    "valid-palindrome": "<strong>Scenario: DNA Sequence Validation</strong><br>A bioinformatics tool needs to check if a DNA sequence string (ignoring spaces and non-alphanumeric characters) reads the same forwards and backwards.",
    "merge-sorted-array": "<strong>Scenario: Database Shard Merging</strong><br>Two distributed database shards have returned sorted lists of user IDs. Merge them in-place into a single sorted list for the frontend.",
    "reverse-string": "<strong>Scenario: Embedded Systems Memory</strong><br>You are programming a micro-controller with extremely limited RAM. Reverse a string buffer in-place without allocating any extra memory.",
    "longest-substring-without-repeating-characters": "<strong>Scenario: Network Packet Analysis</strong><br>You are analyzing a stream of network packets. Find the length of the longest contiguous sequence of packets where no two packets have the same ID.",
    "trapping-rain-water": "<strong>Scenario: Civil Engineering</strong><br>You are designing a city's drainage system. Given an elevation map representing the heights of buildings, calculate how much rainwater can be trapped between them after a storm."
}

def dump_problem(path):
    with open(f"{path}/problem.json") as f:
        problem = json.load(f)
    
    slug = problem["slug"]
    tags = problem.get("tags", [])
    
    # Inject tags for known ones if missing
    if slug in ["two-sum", "group-anagrams", "top-k-frequent-elements", "valid-parentheses"]:
        if "hash-map" not in tags: tags.append("hash-map")
    if slug in ["valid-palindrome", "merge-sorted-array", "reverse-string", "longest-substring-without-repeating-characters", "trapping-rain-water"]:
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

# Two pointers
palindrome = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/valid-palindrome")
merge_sorted = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/merge-sorted-array")
reverse_string = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/reverse-string")
longest_sub = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/longest-substring-without-repeating-characters")
trapping_rain = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/trapping-rain-water")

with open("/Users/vuelancer/Downloads/codewar-offline/dump.json", "w") as f:
    json.dump([two_sum, group_anagrams, top_k, valid_paren, palindrome, merge_sorted, reverse_string, longest_sub, trapping_rain], f, indent=2)
