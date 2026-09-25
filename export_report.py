import os
import csv
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load database URL from .env
load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL", "")

def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    # Use standard psycopg2 for synchronous execution
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    # If it was already set to psycopg (async), revert it to psycopg2 since we are not using async here
    if "+psycopg://" in url:
         url = url.replace("+psycopg://", "+psycopg2://")
    return url

def main():
    if not DATABASE_URL:
        print("Error: POSTGRES_URL not found in .env file.")
        return

    normalized_url = _normalize(DATABASE_URL)
    engine = create_engine(normalized_url)

    # SQL query to get the max stage per student per problem from both backup tables
    query = """
    SELECT 
        s.id AS student_id,
        s.name,
        s.email,
        s.college_id,
        sub.problem_slug,
        MAX(sub.stage) AS max_stage
    FROM (
        SELECT student_id, problem_slug, stage FROM codewar_submissions_backup
        UNION
        SELECT student_id, problem_slug, stage FROM codewar_submissions_backup2
    ) sub
    JOIN codewar_students s ON s.id = sub.student_id
    GROUP BY s.id, s.name, s.email, s.college_id, sub.problem_slug
    ORDER BY s.name, sub.problem_slug;
    """

    print("Executing query to fetch data from backup tables...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()

        csv_filename = "student_submissions_report.csv"
        
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(columns)
            # Write rows
            for row in rows:
                writer.writerow(row)
                
        print(f"Success! Generated CSV report: {csv_filename}")
        print(f"Total records exported: {len(rows)}")

    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    main()
