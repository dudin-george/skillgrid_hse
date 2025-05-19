import sys
import os
import json
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.models.models import SkillPreset, SkillPresetSkill

# Define the skill presets data
SKILL_PRESETS_DATA = [
    {
      "name": "Python Backend Developer - Junior",
      "description": "Entry-level backend developer with foundational Python knowledge. Able to work with data types, control flow, basic functions, and simple APIs.",
      "complexity_level": 1,
      "is_active": True,
      "skill_ids": [
        "c5fb1480-a53f-4165-aa95-acc95840408d",  # Data Types
        "ee5d2bbb-e5f0-4f9c-94ed-b765778d4cbd",  # Control Flow
        "5da48fc3-ebe3-4eb2-a085-4acd7586fe67",  # Loops
        "d625ef53-b95c-4a03-bc08-50fb90520482",  # Functions
        "ad898f87-16d3-4efc-99c9-db09e3e28cee",  # Modules
        "b921a767-013a-443c-8749-11c198eff7a5"   # FastAPI Routing
      ]
    },
    {
      "name": "Python Backend Developer - Middle",
      "description": "Mid-level developer able to implement APIs, manage errors, and design moderately complex systems using Python and FastAPI.",
      "complexity_level": 2,
      "is_active": True,
      "skill_ids": [
        "c5fb1480-a53f-4165-aa95-acc95840408d",  # Data Types
        "5da48fc3-ebe3-4eb2-a085-4acd7586fe67",  # Loops
        "d625ef53-b95c-4a03-bc08-50fb90520482",  # Functions
        "c254ac12-fedd-4b3a-8121-6a0b739de6a1",  # Exceptions
        "4d771c45-19d5-4b8c-bafc-a7e13ac4ea36",  # Comprehensions
        "30f46d1c-726f-4654-8e9e-425c774a834a",  # Typing
        "b921a767-013a-443c-8749-11c198eff7a5",  # FastAPI Routing
        "0b84d40a-b72a-4424-a632-c85783313322",  # FastAPI Request Handling
        "20940f5f-11e1-4886-aa9d-2e04e0f32c99"   # FastAPI Error Handling
      ]
    },
    {
      "name": "Python Backend Developer - Senior",
      "description": "Senior backend engineer with deep expertise in Python, FastAPI, and production-level API development including concurrency, security, and testing.",
      "complexity_level": 3,
      "is_active": True,
      "skill_ids": [
        "d625ef53-b95c-4a03-bc08-50fb90520482",  # Functions
        "df7004eb-b9e4-404f-b597-3a6faaa298ce",  # Classes/OOP
        "30f46d1c-726f-4654-8e9e-425c774a834a",  # Typing
        "acf1acc8-de1d-49f0-9700-a3686f735f0d",  # Concurrency
        "554acb5c-d233-4a73-8b14-64d3e0541957",  # Decorators
        "2bfab7fc-a405-4184-9256-f7aaa5541cf6",  # Testing
        "f603d026-596a-4e47-88c1-7be21edd3033",  # OpenAPI/Docs
        "e260e9c2-82b9-47fb-ba5b-df94fcf3ace4",  # DI in FastAPI
        "6312d9a8-4f18-456c-b445-53cbb9a6bca3",  # Security in FastAPI
        "3af9ef07-2fde-49db-967c-14e257ccbde4"   # Middleware
      ]
    },
    {
      "name": "Data Scientist - Junior",
      "description": "Junior data scientist familiar with Python basics, data manipulation using Pandas, and data exploration using visual summaries.",
      "complexity_level": 1,
      "is_active": True,
      "skill_ids": [
        "c5fb1480-a53f-4165-aa95-acc95840408d",  # Data Types
        "5da48fc3-ebe3-4eb2-a085-4acd7586fe67",  # Loops
        "d625ef53-b95c-4a03-bc08-50fb90520482",  # Functions
        "eef965ca-2a19-4884-9025-eb2fbeeb634f",  # Pandas DataFrames
        "441cb3ee-d67c-4d85-9c13-2e8fe72d6661",  # Pandas Indexing
        "59b69893-f96e-412f-a9bc-65e5966958bc",  # Pandas Manipulation
        "a33051be-8e2e-4f5f-a95d-51a486125887"   # NumPy Array Creation
      ]
    },
    {
      "name": "Data Scientist - Middle",
      "description": "Mid-level data scientist proficient in data processing, feature engineering, SQL for data access, and statistical analysis.",
      "complexity_level": 2,
      "is_active": True,
      "skill_ids": [
        "eef965ca-2a19-4884-9025-eb2fbeeb634f",  # Pandas DataFrames
        "59b69893-f96e-412f-a9bc-65e5966958bc",  # Pandas Manipulation
        "a0c96700-335f-4a2c-b3a6-23a20c6eb6c4",  # Pandas Aggregation
        "6cedcf45-0861-4205-8c9d-0a8cea01b442",  # Pandas Cleaning
        "441cb3ee-d67c-4d85-9c13-2e8fe72d6661",  # Pandas Indexing
        "821d6eea-cde4-4082-8e62-c91149c9e565",  # Pandas Datetime
        "5ef4eb3a-0247-40fa-ba9c-cf13c964d7b9",  # SQL Basic Queries
        "e92c2eb2-e3e1-4830-a09f-97080b00dde7"   # SQL Filtering
      ]
    },
    {
      "name": "Data Scientist - Senior",
      "description": "Senior data scientist with end-to-end project capability, from data pipeline to ML model design, optimization, and deployment.",
      "complexity_level": 3,
      "is_active": True,
      "skill_ids": [
        "eef965ca-2a19-4884-9025-eb2fbeeb634f",  # Pandas DataFrames
        "6cedcf45-0861-4205-8c9d-0a8cea01b442",  # Pandas Cleaning
        "a0c96700-335f-4a2c-b3a6-23a20c6eb6c4",  # Pandas Aggregation
        "20162a08-3210-4ca7-a3ef-dd6e58bbe184",  # Merge/Join
        "73540d68-ca7e-443b-bb1f-9d511ea6535f",  # NumPy Indexing
        "5d2b36db-91c9-4b86-adcc-0d292bdf776c",  # NumPy Statistics  # Algorithms and DS
        "98642b24-51c0-4c5a-970f-145e724ce389",  # SQL Grouping/Aggregation
        "787c72ac-6b54-4b32-ac23-a9c2dea2672d",  # SQL Subqueries
        "558489c0-54f9-45b4-8a43-784bd0cb1586"   # Dynamic Programming
      ]
    }
]

def load_skill_presets():
    """
    Load the skill presets and their mappings into the database
    """
    # Get the database session
    db = next(get_db())
    
    try:
        print("Starting skill presets data loading...")
        now = datetime.utcnow()
        
        for preset_data in SKILL_PRESETS_DATA:
            # Create skill preset
            preset = SkillPreset(
                id=uuid4(),
                name=preset_data["name"],
                description=preset_data["description"],
                complexity_level=preset_data["complexity_level"],
                is_active=preset_data["is_active"],
                created_at=now,
                updated_at=now
            )
            db.add(preset)
            db.flush()  # Flush to get the ID
            
            print(f"Created skill preset: {preset.name}")
            
            # Create skill mappings
            for i, skill_id_str in enumerate(preset_data["skill_ids"]):
                try:
                    skill_id = UUID(skill_id_str)
                    
                    # Importance defaults to middle value with slight variance
                    importance = 3
                    if i < len(preset_data["skill_ids"]) // 3:
                        importance = 5  # More important skills
                    elif i >= 2 * len(preset_data["skill_ids"]) // 3:
                        importance = 2  # Less important skills
                    
                    skill_preset_skill = SkillPresetSkill(
                        id=uuid4(),
                        skill_preset_id=preset.id,
                        skill_id=skill_id,
                        importance=importance,
                        created_at=now
                    )
                    db.add(skill_preset_skill)
                    print(f"  Added skill mapping: {skill_id_str} (importance: {importance})")
                except ValueError as e:
                    print(f"  Error with skill ID {skill_id_str}: {str(e)}")
        
        # Commit all changes
        db.commit()
        print("Skill presets data loaded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error loading skill presets data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_skill_presets() 