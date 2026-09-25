import os
import csv
import json
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import google.generativeai as genai
from pydantic import BaseModel, Field

# Load database URL and set up Gemini API
load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not found.")
    print("Please set it before running this script: export GEMINI_API_KEY='your-key'")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
# Use gemini-1.5-flash for faster and cheaper evaluation
model = genai.GenerativeModel('gemini-1.5-flash')

class EvaluationResult(BaseModel):
    score: int = Field(description="1 if the logical approach is generally correct to solve the problem, 0 if it is completely wrong or just boilerplate.")
    feedback: str = Field(description="A very brief 1-sentence explanation of why the logic is correct or incorrect.")

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
    
    end_idx = content.find("];", start_idx)
    if end_idx == -1:
        end_idx = content.find("]\n", start_idx)
        
    json_str = content[start_idx:end_idx+1]
    return json.loads(json_str)

def evaluate_code_logic(statement: str, language: str, code: str) -> dict:
    prompt = f"""
You are an expert programming instructor. Your job is to statically analyze a student's code and determine if the underlying *logic* and *algorithm* they wrote is generally correct and attempts to solve the given problem statement. 
Ignore minor syntax errors, missing imports, or minor edge cases. We just want to know if they understood the problem and wrote a valid approach.
If they just submitted the default boilerplate, or an empty function, score it as 0.

Problem Statement:
{statement}

Language: {language}
Student Code:
```
{code}
```

Evaluate the logic and return a score of 1 (correct approach) or 0 (incorrect or boilerplate).
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=EvaluationResult,
                temperature=0.0,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error evaluating code: {e}")
        return {"score": 0, "feedback": f"API Error: {str(e)}"}

def get_submissions():
    normalized_url = _normalize(DATABASE_URL)
    engine = create_engine(normalized_url)
    
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
    print("Loading problem statements from data.js...")
    problems_data = load_problems_from_data_js()
    
    statement_map = {}
    for p in problems_data:
        slug = p["problem"]["slug"]
        statement_map[slug] = {}
        for idx, stage in enumerate(p["stages"]):
            stage_num = idx + 1
            # Extract plain text statement without HTML tags
            stmt = stage.get("statement", "").replace("<strong>", "").replace("</strong>", "").replace("<code>", "`").replace("</code>", "`").replace("<br>", "\n")
            statement_map[slug][stage_num] = stmt
            
    print("Fetching submissions from database...")
    submissions = get_submissions()
    print(f"Found {len(submissions)} unique submissions to evaluate.")
    
    csv_filename = "ai_graded_report.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Student ID", "Name", "Email", "College ID", "Problem", "Stage", "Language", "Score", "AI Feedback"])
        
        for i, sub in enumerate(submissions):
            student_id = sub.student_id
            slug = sub.problem_slug
            stage = sub.stage
            code = sub.code
            lang = sub.language
            
            statement = statement_map.get(slug, {}).get(stage, "")
            if not statement:
                print(f"Skipping {student_id} {slug} stage {stage} - no statement found.")
                continue
                
            print(f"[{i+1}/{len(submissions)}] AI Evaluating {sub.name} - {slug} Stage {stage} ({lang})")
            
            # Rate limit backoff for standard Gemini free tier (15 RPM limits might apply depending on account)
            # Sleep 4 seconds to be safe
            time.sleep(4)
            
            result = evaluate_code_logic(statement, lang, code)
            
            writer.writerow([
                student_id, sub.name, sub.email, sub.college_id, 
                slug, stage, lang, result.get("score", 0), result.get("feedback", "")
            ])
            file.flush() 
            
    print(f"\nAI Grading complete! Report saved to {csv_filename}")

if __name__ == "__main__":
    main()
