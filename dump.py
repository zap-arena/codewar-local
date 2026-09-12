import json
import os

def dump_problem(path):
    with open(f"{path}/problem.json") as f:
        problem = json.load(f)
    
    stages_data = []
    for stage in problem["stages"]:
        stage_order = stage["stageOrder"]
        tc_dir = f"{path}/testcases/stage-{stage_order}"
        samples = []
        for i in range(1, 3):
            tc_file = f"{tc_dir}/tc{i}.json"
            if os.path.exists(tc_file):
                with open(tc_file) as tf:
                    tc = json.load(tf)
                    samples.append({
                        "input": tc["input"],
                        "output": tc["expected_output"]
                    })
        stages_data.append({
            "title": stage["title"],
            "complexity": stage["expectedComplexity"],
            "statement": stage["statement"],
            "samples": samples
        })
    
    return {
        "problem": {
            "title": problem["title"],
            "slug": problem["slug"]
        },
        "stages": stages_data
    }

grid = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/grid-traversal-progressive")
stock = dump_problem("/Users/vuelancer/Downloads/zap-problem-bank/problems/buy-sell-stock-progressive")

with open("/Users/vuelancer/Downloads/codewar-offline/dump.json", "w") as f:
    json.dump([grid, stock], f, indent=2)
