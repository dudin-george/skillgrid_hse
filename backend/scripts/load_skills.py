import sys
import os
import json
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.models.models import Domain, Skill, SubSkill

# Define the skills data
SKILLS_DATA = {
  "Python": {
    "Data Types": [
      "int", "float", "string", "bool", "list", "tuple", "dict", "set", "NoneType"
    ],
    "Control Flow": [
      "if", "else", "elif", "match", "ternary operator"
    ],
    "Loops": [
      "for", "while", "break", "continue", "enumerate", "zip"
    ],
    "Functions": [
      "def", "return", "lambda", "args", "kwargs", "recursion"
    ],
    "Exceptions": [
      "try", "except", "finally", "raise", "assert"
    ],
    "Comprehensions": [
      "list comprehension", "dict comprehension", "set comprehension"
    ],
    "Classes/OOP": [
      "class", "__init__", "self", "inheritance", "encapsulation", "staticmethod", "classmethod"
    ],
    "File I/O": [
      "open", "read", "write", "with", "file modes"
    ],
    "Modules": [
      "import", "from import", "as", "standard library", "pip packages"
    ],
    "Decorators": [
      "@decorator", "function decorators", "class decorators"
    ],
    "Typing": [
      "type hints", "Optional", "Union", "List", "Dict"
    ],
    "Concurrency": [
      "threading", "asyncio", "await", "async def", "concurrent.futures"
    ],
    "Testing": [
      "unittest", "pytest", "mock", "assert statements"
    ]
  },
  "FastAPI": {
    "Routing": [
      "@app.get", "@app.post", "path parameters", "query parameters"
    ],
    "Request Handling": [
      "Request body", "pydantic models", "Form data", "File uploads"
    ],
    "Responses": [
      "Response model", "status_code", "JSONResponse", "RedirectResponse"
    ],
    "Validation": [
      "pydantic validation", "Field constraints", "Custom validators"
    ],
    "Middleware": [
      "custom middleware", "request/response cycle"
    ],
    "Dependency Injection": [
      "Depends", "Reusable dependencies", "Security dependencies"
    ],
    "Background Tasks": [
      "BackgroundTasks", "async background jobs"
    ],
    "Error Handling": [
      "HTTPException", "Custom exception handlers"
    ],
    "Security": [
      "OAuth2", "JWT", "Security schemes", "Scopes"
    ],
    "OpenAPI/Docs": [
      "OpenAPI schema", "Swagger UI", "ReDoc"
    ]
  },
  "SQL": {
    "Basic Queries": [
      "SELECT", "FROM", "WHERE", "ORDER BY", "LIMIT", "OFFSET"
    ],
    "Filtering": [
      "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE"
    ],
    "Joins": [
      "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"
    ],
    "Grouping/Aggregation": [
      "GROUP BY", "HAVING", "COUNT", "SUM", "AVG", "MIN", "MAX"
    ],
    "Subqueries": [
      "Subquery in SELECT", "Subquery in WHERE", "Correlated subquery"
    ],
    "Modifying Data": [
      "INSERT", "UPDATE", "DELETE"
    ],
    "DDL": [
      "CREATE TABLE", "ALTER TABLE", "DROP TABLE"
    ],
    "Constraints": [
      "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "DEFAULT"
    ],
    "Indexes": [
      "CREATE INDEX", "DROP INDEX", "Composite index"
    ],
    "Transactions": [
      "BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT"
    ],
    "Views/CTEs": [
      "CREATE VIEW", "WITH (CTE)", "Recursive CTE"
    ],
    "Functions & Procedures": [
      "Stored procedures", "User-defined functions", "Triggers"
    ],
    "Performance": [
      "EXPLAIN", "Query optimization", "Indexes"
    ]
  },
  "Pandas": {
    "DataFrames": [
      "create", "inspect", "describe", "shape", "info", "head", "tail"
    ],
    "Indexing": [
      "loc", "iloc", "boolean indexing", "slice", "column selection"
    ],
    "Manipulation": [
      "add column", "drop column", "rename", "apply", "map"
    ],
    "Aggregation": [
      "groupby", "sum", "mean", "count", "agg", "pivot_table"
    ],
    "Cleaning": [
      "fillna", "dropna", "replace", "duplicated", "astype"
    ],
    "Merge/Join": [
      "merge", "join", "concat", "append"
    ],
    "Datetime": [
      "to_datetime", "dt accessor", "resample"
    ],
    "Export": [
      "to_csv", "to_excel", "to_json"
    ]
  },
  "NumPy": {
    "Array Creation": [
      "array", "zeros", "ones", "arange", "linspace", "random"
    ],
    "Indexing": [
      "basic", "slicing", "boolean", "fancy"
    ],
    "Math Operations": [
      "add", "subtract", "multiply", "divide", "power"
    ],
    "Linear Algebra": [
      "dot", "matmul", "inv", "transpose", "svd", "eig"
    ],
    "Statistics": [
      "mean", "median", "std", "var", "sum", "min", "max"
    ]
  },
  "Linux": {
    "File System": [
      "ls", "cd", "pwd", "mkdir", "rm", "cp", "mv", "find"
    ],
    "Permissions": [
      "chmod", "chown", "groups", "umask"
    ],
    "Processes": [
      "ps", "top", "kill", "jobs", "bg", "fg"
    ],
    "Networking": [
      "ping", "curl", "wget", "netstat", "ss", "ssh"
    ],
    "Package Management": [
      "apt", "yum", "dpkg", "snap"
    ],
    "Text Tools": [
      "cat", "less", "head", "tail", "grep", "awk", "sed"
    ],
    "Archives": [
      "tar", "zip", "gzip", "unzip"
    ],
    "Crontab": [
      "crontab -e", "crontab -l"
    ]
  },
  "Git": {
    "Basics": [
      "init", "clone", "add", "commit", "status", "log"
    ],
    "Branches": [
      "branch", "checkout", "merge", "rebase"
    ],
    "Remote": [
      "remote", "fetch", "pull", "push"
    ],
    "Tags": [
      "tag", "push --tags"
    ],
    "Stashing": [
      "stash", "stash apply", "stash pop"
    ],
    "Reset/Revert": [
      "reset", "revert", "clean"
    ],
    "Hooks": [
      "pre-commit", "post-commit", "custom scripts"
    ]
  },
  "Docker": {
    "Basics": [
      "images", "containers", "run", "stop", "rm", "exec", "logs"
    ],
    "Dockerfile": [
      "FROM", "COPY", "RUN", "CMD", "ENTRYPOINT", "EXPOSE"
    ],
    "Volumes": [
      "bind mounts", "named volumes", "anonymous volumes"
    ],
    "Networking": [
      "bridge", "host", "overlay", "port mapping"
    ],
    "Compose": [
      "docker-compose.yml", "services", "volumes", "networks"
    ],
    "Optimization": [
      "multi-stage builds", "caching", "minimizing image size"
    ]
  },
  "REST API": {
    "Methods": [
      "GET", "POST", "PUT", "PATCH", "DELETE"
    ],
    "Status Codes": [
      "200", "201", "204", "400", "401", "403", "404", "500"
    ],
    "Authentication": [
      "API Key", "JWT", "OAuth2"
    ],
    "Pagination": [
      "limit/offset", "page/size", "next/prev links"
    ],
    "Versioning": [
      "URI versioning", "Header versioning"
    ],
    "Rate Limiting": [
      "429 Too Many Requests", "Retry-After header"
    ]
  },
  "Algorithms and Data Structures": {
    "Sorting": [
      "bubble", "selection", "insertion", "merge", "quick", "heap"
    ],
    "Searching": [
      "linear", "binary", "DFS", "BFS"
    ],
    "Data Structures": [
      "array", "linked list", "stack", "queue", "heap", "hash map"
    ],
    "Graphs": [
      "adjacency list", "DFS", "BFS", "Dijkstra", "A*", "topological sort"
    ],
    "Trees": [
      "binary tree", "BST", "AVL", "Trie"
    ],
    "Recursion": [
      "factorial", "fibonacci", "backtracking"
    ],
    "Dynamic Programming": [
      "memoization", "tabulation", "knapsack", "LCS"
    ]
  }
}

def load_skills_data():
    """
    Load the skills data into the database
    """
    # Get the database session
    db = next(get_db())
    
    # Track created domains and skills for reference
    domain_map = {}
    skill_map = {}
    
    try:
        print("Starting skills data loading...")
        
        # Set level calculations based on domain hierarchy
        domain_levels = {
            "Python": 5,
            "FastAPI": 4,
            "SQL": 4, 
            "Pandas": 3,
            "NumPy": 3,
            "Linux": 3,
            "Git": 3,
            "Docker": 3,
            "REST API": 4,
            "Algorithms and Data Structures": 5
        }
        
        # Create domains first
        for domain_name, skills in SKILLS_DATA.items():
            # Create domain
            domain = Domain(
                id=uuid4(),
                name=domain_name,
                description=f"{domain_name} domain for skills assessment",
                is_active=True
            )
            db.add(domain)
            db.flush()  # Flush to get the ID
            
            domain_map[domain_name] = domain.id
            print(f"Created domain: {domain_name}")
            
            # Create skills for this domain
            for skill_name, subskills in skills.items():
                # Get appropriate level for this skill (1-5)
                base_level = domain_levels.get(domain_name, 3)
                
                # Create skill
                skill = Skill(
                    id=uuid4(),
                    domain_id=domain.id,
                    name=skill_name,
                    level=base_level,
                    requirements=f"Knowledge of {skill_name} in {domain_name}",
                    is_active=True
                )
                db.add(skill)
                db.flush()  # Flush to get the ID
                
                skill_map[f"{domain_name}.{skill_name}"] = skill.id
                print(f"  Created skill: {skill_name}")
                
                # Create subskills for this skill
                for subskill_name in subskills:
                    subskill = SubSkill(
                        id=uuid4(),
                        skill_id=skill.id,
                        name=subskill_name,
                        is_active=True
                    )
                    db.add(subskill)
                    print(f"    Created subskill: {subskill_name}")
        
        # Commit all changes
        db.commit()
        print("Skills data loaded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error loading skills data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_skills_data() 