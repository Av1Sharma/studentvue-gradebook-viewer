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
    print("Raw gradebook response:", json.dumps(gradebook, indent=2))
    
    # Validate and clean the response
    if not isinstance(gradebook, dict):
        raise ValueError(f"Invalid gradebook response format: {type(gradebook)}")
        
    if 'Gradebook' not in gradebook:
        raise ValueError("No gradebook data in response")
        
    courses = gradebook['Gradebook'].get('Courses', {})
    print("Courses data:", json.dumps(courses, indent=2))
    
    if not isinstance(courses, dict):
        raise ValueError(f"Invalid courses data format: {type(courses)}")
        
    course_list = courses.get('Course', [])
    print("Course list:", json.dumps(course_list, indent=2))
    
    if not isinstance(course_list, list):
        course_list = [course_list]
        
    # Clean and validate each course
    for course in course_list:
        if not isinstance(course, dict):
            print(f"Skipping invalid course: {type(course)}")
            continue
            
        # Ensure Marks is a list
        marks = course.get('Marks', {})
        print(f"Course marks before processing: {json.dumps(marks, indent=2)}")
        
        if isinstance(marks, dict):
            mark_list = marks.get('Mark', [])
            if not isinstance(mark_list, list):
                mark_list = [mark_list]
            course['Marks'] = {'Mark': mark_list}
            
        # Ensure Assignments is a list
        assignments = course.get('Assignments', {})
        print(f"Course assignments before processing: {json.dumps(assignments, indent=2)}")
        
        if isinstance(assignments, dict):
            assignment_list = assignments.get('Assignment', [])
            if not isinstance(assignment_list, list):
                assignment_list = [assignment_list]
            course['Assignments'] = {'Assignment': assignment_list}
    
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