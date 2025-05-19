import sys
import os
import json
from datetime import datetime
import uuid

# Add the parent directory to the path to be able to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.models.models import Task, TaskSubSkill, TaskTest, DifficultyLevel
from app.db.database import SessionLocal, engine
from app.models.models import Base, SubSkill

def create_sample_tasks():
    """Create sample coding tasks for the assessment system"""
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # First, clean up any existing tasks
        print("Cleaning up existing tasks...")
        db.query(TaskTest).delete()
        db.query(TaskSubSkill).delete()
        db.query(Task).delete()
        db.commit()
        
        print("Creating sample tasks...")
        
        # Task 1: Calculate Factorial
        factorial_task = Task(
            title="Calculate Factorial",
            description="Write a function to calculate the factorial of a given non-negative integer n. The factorial of n is the product of all positive integers less than or equal to n.",
            instructions="Implement the `factorial` function that takes a non-negative integer n and returns n!",
            difficulty=DifficultyLevel.EASY,
            time_limit_minutes=10,
            points=10,
            examples=json.dumps([
                {
                    "input": "5",
                    "output": "120",
                    "explanation": "5! = 5 * 4 * 3 * 2 * 1 = 120"
                },
                {
                    "input": "0",
                    "output": "1",
                    "explanation": "0! is defined as 1"
                }
            ]),
            solution_template="def factorial(n):\n    # Your code here\n    pass\n\n# Test\nresult = factorial(5)\nprint(result)",
            solution_criteria="The solution should handle edge cases such as 0 and should be efficient."
        )
        db.add(factorial_task)
        db.flush()  # To get the ID
        
        # Add test cases for this task
        test_cases = [
            {"input_data": "5", "expected_output": "120", "is_hidden": False},
            {"input_data": "0", "expected_output": "1", "is_hidden": False},
            {"input_data": "10", "expected_output": "3628800", "is_hidden": True},
            {"input_data": "1", "expected_output": "1", "is_hidden": True}
        ]
        
        for tc in test_cases:
            db.add(TaskTest(
                task_id=factorial_task.id,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"]
            ))
        
        # Task 2: Find Prime Numbers
        prime_task = Task(
            title="Find Prime Numbers",
            description="Write a function to find all prime numbers up to a given number n. A prime number is a natural number greater than 1 that is not divisible by any natural number other than 1 and itself.",
            instructions="Implement the `find_primes` function that takes a positive integer n and returns a list of all prime numbers less than or equal to n.",
            difficulty=DifficultyLevel.MEDIUM,
            time_limit_minutes=15,
            points=15,
            examples=json.dumps([
                {
                    "input": "10",
                    "output": "[2, 3, 5, 7]",
                    "explanation": "The prime numbers up to 10 are 2, 3, 5, and 7."
                },
                {
                    "input": "20",
                    "output": "[2, 3, 5, 7, 11, 13, 17, 19]",
                    "explanation": "The prime numbers up to 20."
                }
            ]),
            solution_template="def find_primes(n):\n    # Your code here\n    pass\n\n# Test\nresult = find_primes(10)\nprint(result)",
            solution_criteria="The solution should be efficient. Consider using the Sieve of Eratosthenes algorithm for better performance."
        )
        db.add(prime_task)
        db.flush()
        
        # Add test cases for this task
        test_cases = [
            {"input_data": "10", "expected_output": "[2, 3, 5, 7]", "is_hidden": False},
            {"input_data": "20", "expected_output": "[2, 3, 5, 7, 11, 13, 17, 19]", "is_hidden": False},
            {"input_data": "30", "expected_output": "[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]", "is_hidden": True},
            {"input_data": "1", "expected_output": "[]", "is_hidden": True}
        ]
        
        for tc in test_cases:
            db.add(TaskTest(
                task_id=prime_task.id,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"]
            ))
        
        # Task 3: Binary Search
        binary_search_task = Task(
            title="Binary Search Algorithm",
            description="Implement the binary search algorithm to efficiently find the index of a target value in a sorted array.",
            instructions="Implement the `binary_search` function that takes a sorted list of integers `nums` and a target value `target`. Return the index of the target if found, otherwise return -1.",
            difficulty=DifficultyLevel.MEDIUM,
            time_limit_minutes=20,
            points=20,
            examples=json.dumps([
                {
                    "input": "nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], target = 5",
                    "output": "4",
                    "explanation": "The number 5 is at index 4 (0-indexed)."
                },
                {
                    "input": "nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], target = 11",
                    "output": "-1",
                    "explanation": "The number 11 is not in the array, so return -1."
                }
            ]),
            solution_template="def binary_search(nums, target):\n    # Your code here\n    pass\n\n# Test\nnums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\nresult = binary_search(nums, 5)\nprint(result)",
            solution_criteria="The solution should use the binary search algorithm, which has O(log n) time complexity. Iterative or recursive approaches are both acceptable."
        )
        db.add(binary_search_task)
        db.flush()
        
        # Add test cases for this task
        test_cases = [
            {"input_data": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5", "expected_output": "4", "is_hidden": False},
            {"input_data": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11", "expected_output": "-1", "is_hidden": False},
            {"input_data": "[1, 3, 5, 7, 9, 11], 7", "expected_output": "3", "is_hidden": True},
            {"input_data": "[], 1", "expected_output": "-1", "is_hidden": True}
        ]
        
        for tc in test_cases:
            db.add(TaskTest(
                task_id=binary_search_task.id,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"]
            ))
        
        # Task 4: Reverse a Linked List
        linked_list_task = Task(
            title="Reverse a Linked List",
            description="Write a function to reverse a singly linked list. A linked list is a data structure consisting of nodes where each node contains a value and a pointer to the next node.",
            instructions="Implement the `reverse_linked_list` function that takes the head node of a linked list and returns the head of the reversed linked list.",
            difficulty=DifficultyLevel.HARD,
            time_limit_minutes=25,
            points=25,
            examples=json.dumps([
                {
                    "input": "1 -> 2 -> 3 -> 4 -> 5 -> NULL",
                    "output": "5 -> 4 -> 3 -> 2 -> 1 -> NULL",
                    "explanation": "The linked list is reversed."
                }
            ]),
            solution_template="class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_linked_list(head):\n    # Your code here\n    pass\n\n# Test function to create a linked list from a list of values\ndef create_linked_list(values):\n    dummy = ListNode(0)\n    current = dummy\n    for val in values:\n        current.next = ListNode(val)\n        current = current.next\n    return dummy.next\n\n# Test function to convert linked list to a list for verification\ndef linked_list_to_list(head):\n    result = []\n    current = head\n    while current:\n        result.append(current.val)\n        current = current.next\n    return result\n\n# Test\nhead = create_linked_list([1, 2, 3, 4, 5])\nreversed_head = reverse_linked_list(head)\nprint(linked_list_to_list(reversed_head))",
            solution_criteria="The solution should reverse the linked list in-place with O(1) space complexity. Both iterative and recursive solutions are acceptable."
        )
        db.add(linked_list_task)
        db.flush()
        
        # Add test cases for this task
        test_cases = [
            {"input_data": "[1, 2, 3, 4, 5]", "expected_output": "[5, 4, 3, 2, 1]", "is_hidden": False},
            {"input_data": "[1]", "expected_output": "[1]", "is_hidden": False},
            {"input_data": "[]", "expected_output": "[]", "is_hidden": True},
            {"input_data": "[1, 2]", "expected_output": "[2, 1]", "is_hidden": True}
        ]
        
        for tc in test_cases:
            db.add(TaskTest(
                task_id=linked_list_task.id,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"]
            ))
        
        # Task 5: SQL Query 
        sql_task = Task(
            title="Write a SQL Query",
            description="Write a SQL query to find the names of all employees who have a higher salary than their manager.",
            instructions="Given two tables `Employee` and `Manager`, write a SQL query to retrieve the names of employees who earn more than their direct manager.",
            difficulty=DifficultyLevel.HARD,
            time_limit_minutes=20,
            points=20,
            examples=json.dumps([
                {
                    "input": "Employee table:\nid | name | manager_id | salary\n1  | Joe  | 2          | 70000\n2  | Sam  | 3          | 60000\n3  | Max  | NULL       | 90000",
                    "output": "name\nJoe",
                    "explanation": "Joe earns 70000 while his manager Sam earns 60000."
                }
            ]),
            solution_template="-- Your SQL query here\n/*\nExample schema:\n\nEmployee table:\nid | name | manager_id | salary\n1  | Joe  | 2          | 70000\n2  | Sam  | 3          | 60000\n3  | Max  | NULL       | 90000\n*/",
            solution_criteria="Your solution should use a self-join on the Employee table to compare employee salaries with their managers' salaries."
        )
        db.add(sql_task)
        db.flush()
        
        # Add test cases for this task (conceptual for SQL)
        test_cases = [
            {"input_data": "Employee table with Joe(70k), Sam(60k), Max(90k)", 
             "expected_output": "Joe", 
             "is_hidden": False}
        ]
        
        for tc in test_cases:
            db.add(TaskTest(
                task_id=sql_task.id,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"],
                is_hidden=tc["is_hidden"]
            ))
        
        # Link tasks to subskills
        print("Linking tasks to subskills...")
        
        # Get some sample subskills to link to tasks
        subskills = db.query(SubSkill).all()
        
        if subskills:
            # Map tasks to appropriate subskills
            # This is just a simple example - in a real app, you'd want to be more precise
            # about which tasks test which specific subskills
            
            programming_subskills = subskills[:5]  # Just grab some subskills
            
            for i, task in enumerate([factorial_task, prime_task, binary_search_task, linked_list_task, sql_task]):
                # Link each task to 2-3 subskills
                for j in range(min(len(programming_subskills), 3)):
                    subskill_index = (i + j) % len(programming_subskills)
                    db.add(TaskSubSkill(
                        task_id=task.id,
                        subskill_id=programming_subskills[subskill_index].id,
                        is_required=(j == 0),  # First subskill is required
                        importance=5 - j  # Decreasing importance
                    ))
        
        # Commit all changes
        db.commit()
        
        print("Sample tasks created successfully!")
        print(f"Created {db.query(Task).count()} tasks with {db.query(TaskTest).count()} test cases and {db.query(TaskSubSkill).count()} subskill links.")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample tasks: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_tasks() 