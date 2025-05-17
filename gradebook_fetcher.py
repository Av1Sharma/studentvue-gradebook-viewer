import os
from typing import Optional
from studentvue import StudentVue
from dotenv import load_dotenv
import json

def setup_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    required_vars = ['STUDENTVUE_USERNAME', 'STUDENTVUE_PASSWORD', 'STUDENTVUE_DOMAIN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def fetch_gradebook(report_period: Optional[int] = None) -> dict:
    """
    Fetch gradebook information from StudentVue
    
    Args:
        report_period (int, optional): Specific report period to fetch. Defaults to None.
    
    Returns:
        dict: Gradebook information
    """
    setup_environment()
    
    # Initialize StudentVue client
    client = StudentVue(
        username=os.getenv('STUDENTVUE_USERNAME'),
        password=os.getenv('STUDENTVUE_PASSWORD'),
        district_domain=os.getenv('STUDENTVUE_DOMAIN')
    )
    
    # Fetch gradebook
    gradebook = client.get_gradebook(report_period=report_period)
    return gradebook

def display_gradebook(gradebook: dict):
    if not gradebook or 'Gradebook' not in gradebook:
        print("No gradebook data available")
        return
    
    courses = gradebook['Gradebook'].get('Courses', {}).get('Course', [])
    if not isinstance(courses, list):
        courses = [courses]
    
    for course in courses:
        print("\n" + "="*50)
        
        title = course.get('@Title', 'N/A')
        teacher = course.get('@Teacher', 'N/A')
        period = course.get('@Period', 'N/A')
        room = course.get('@Room', 'N/A')
        
        print(f"Course: {title}")
        print(f"Teacher: {teacher}")
        print(f"Period: {period}")
        print(f"Room: {room}")
        
        # Get marks/grades
        marks = course.get('Marks', {}).get('Mark', [])
        if not isinstance(marks, list):
            marks = [marks]
            
        for mark in marks:
            mark_name = mark.get('@MarkName', 'N/A')
            # Skip HS-EX2 marking period
            if mark_name == 'HS-EX2':
                continue
                
            calculated_score = mark.get('@CalculatedScoreString', 'N/A')
            raw_score = mark.get('@CalculatedScoreRaw', 'N/A')
            
            print(f"\nMarking Period: {mark_name}")
            print(f"Grade: {calculated_score} ({raw_score}%)")
            
            # Only show grade breakdown for current marking period (HS-MK4)
            if mark_name == 'HS-MK4':
                grade_calc = mark.get('GradeCalculationSummary', {}).get('AssignmentGradeCalc', [])
                if not isinstance(grade_calc, list):
                    grade_calc = [grade_calc]
                    
                print("\nGrade Breakdown:")
                for calc in grade_calc:
                    if calc.get('@Type') != 'TOTAL':
                        print(f"- {calc.get('@Type')}: {calc.get('@WeightedPct')} ({calc.get('@CalculatedMark')})")
        
        # Display assignments
        assignments = course.get('Assignments', {}).get('Assignment', [])
        if not isinstance(assignments, list):
            assignments = [assignments]
        
        if assignments:
            print("\nRecent Assignments:")
            print("-"*30)
            for assignment in assignments:
                name = assignment.get('@Measure', 'N/A')
                type_ = assignment.get('@Type', 'N/A')
                date = assignment.get('@Date', 'N/A')
                due_date = assignment.get('@DueDate', 'N/A')
                score = assignment.get('@DisplayScore', 'N/A')
                notes = assignment.get('@Notes', '')
                
                print(f"Name: {name}")
                print(f"Type: {type_}")
                print(f"Date: {date}")
                print(f"Due Date: {due_date}")
                print(f"Score: {score}")
                if notes:
                    print(f"Notes: {notes}")
                print("-"*30)

def main():
    try:
        # Fetch gradebook for current period
        gradebook = fetch_gradebook()
        display_gradebook(gradebook)
    except Exception as e:
        print(f"Error fetching gradebook: {str(e)}")

if __name__ == "__main__":
    main() 