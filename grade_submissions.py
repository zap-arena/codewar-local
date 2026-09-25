import os
import csv
import json
import time
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL", "")

PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"

def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if "+psycopg://" in url:
         url = url.replace("+psycopg://", "+psycopg2://")
    return url

def load_problems_from_data_js():
    with open("data.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    start_token = "const PROBLEMS = "
    start_idx = content.find(start_token)
    if start_idx == -1:
        raise ValueError("Could not find 'const PROBLEMS =' in data.js")
    
    start_idx += len(start_token)
    
    # We find the matching end brace for the array
    end_idx = content.find("];", start_idx)
    if end_idx == -1:
        end_idx = content.find("]\n", start_idx)
        
    if end_idx == -1:
        raise ValueError("Could not find end of PROBLEMS array")
        
    json_str = content[start_idx:end_idx+1]
    
    try:
        return json.loads(json_str)
    except Exception as e:
        print("Failed to parse JSON from data.js. String was:", json_str[:100], "...")
        raise e

def run_code_on_piston(language, code, stdin=""):
    # Map 'javascript' -> 'js' or 'javascript' in piston
    lang_map = {
        "python": "python",
        "javascript": "javascript",
        "java": "java",
        "cpp": "cpp",
        "c": "c"
    }
    
    if language not in lang_map:
        return {"output": "Unsupported language", "code": 1}
        
    payload = {
        "language": lang_map[language],
        "version": "*",
        "files": [{"content": code}],
        "stdin": stdin
    }
    
    try:
        res = requests.post(PISTON_API_URL, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            run_result = data.get("run", {})
            return {
                "output": run_result.get("output", ""),
                "code": run_result.get("code", 0),
                "signal": run_result.get("signal", None)
            }
        else:
            return {"output": f"API Error: {res.status_code}", "code": -1}
    except Exception as e:
        return {"output": f"Execution Exception: {str(e)}", "code": -1}

def get_submissions():
    normalized_url = _normalize(DATABASE_URL)
    engine = create_engine(normalized_url)
    
    # Get the latest submission for each stage using ROW_NUMBER to avoid duplicates
    query = """
    WITH CombinedSubmissions AS (
        SELECT student_id, problem_slug, stage, language, code, submitted_at
        FROM codewar_submissions_backup
        UNION ALL
        SELECT student_id, problem_slug, stage, language, code, submitted_at
        FROM codewar_submissions_backup2
    ),
    RankedSubmissions AS (
        SELECT 
            cs.*,
            ROW_NUMBER() OVER(PARTITION BY student_id, problem_slug, stage ORDER BY submitted_at DESC) as rn
        FROM CombinedSubmissions cs
    )
    SELECT 
        s.id AS student_id,
        s.name,
        s.email,
        s.college_id,
        rs.problem_slug,
        rs.stage,
        rs.language,
        rs.code
    FROM RankedSubmissions rs
    JOIN codewar_students s ON s.id = rs.student_id
    WHERE rs.rn = 1 
      AND rs.problem_slug IN ('contains-duplicate-progressive', 'grid-traversal-progressive')
    ORDER BY s.email, rs.problem_slug, rs.stage;
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()

def main():
    print("Loading testcases from data.js...")
    problems_data = load_problems_from_data_js()
    
    # Build a quick lookup for testcases
    # testcases_map[problem_slug][stage_num_1_indexed] = [ {input, output}, ... ]
    testcases_map = {}
    for p in problems_data:
        slug = p["problem"]["slug"]
        testcases_map[slug] = {}
        for idx, stage in enumerate(p["stages"]):
            stage_num = idx + 1
            testcases_map[slug][stage_num] = stage.get("samples", [])
            
    print("Fetching submissions from database...")
    submissions = get_submissions()
    print(f"Found {len(submissions)} unique submissions to grade.")
    
    # Track results: student_id -> problem_slug -> { 'name':, 'email':, 'college_id':, 'stages_passed': X, 'total_stages_submitted': Y }
    report_data = {}
    
    csv_filename = "graded_report.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Student ID", "Name", "Email", "College ID", "Problem", "Stage", "Language", "Passed Samples", "Total Samples", "Stage Score"])
        
        for i, sub in enumerate(submissions):
            student_id = sub.student_id
            slug = sub.problem_slug
            stage = sub.stage
            code = sub.code
            lang = sub.language
            
            samples = testcases_map.get(slug, {}).get(stage, [])
            if not samples:
                print(f"Skipping {student_id} {slug} stage {stage} - no testcases found.")
                continue
                
            print(f"[{i+1}/{len(submissions)}] Grading {sub.name} - {slug} Stage {stage} ({lang})")
            
            passed_samples = 0
            for sample in samples:
                # Sleep to respect Piston API rate limit (5 req/sec max)
                time.sleep(0.3)
                
                expected_out = sample['output'].strip()
                res = run_code_on_piston(lang, code, sample['input'])
                
                actual_out = res['output'].strip()
                
                # Check if it passes
                if res['code'] == 0 and actual_out == expected_out:
                    passed_samples += 1
                    
            stage_score = 1 if passed_samples == len(samples) else 0
            
            writer.writerow([
                student_id, sub.name, sub.email, sub.college_id, 
                slug, stage, lang, passed_samples, len(samples), stage_score
            ])
            file.flush() # flush so user can tail the file
            
    print(f"\nGrading complete! Report saved to {csv_filename}")

if __name__ == "__main__":
    main()
