import streamlit as st
import os
from gradebook_fetcher import fetch_gradebook, display_gradebook
from dotenv import load_dotenv

# Set page config
st.set_page_config(
    page_title="StudentVue Gradebook Viewer",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .course-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .grade-section {
        margin: 1rem 0;
    }
    .assignment-section {
        margin-top: 1rem;
    }
    hr {
        margin: 0.5rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📚 StudentVue Gradebook Viewer")

    try:
        # Hardcoded credentials for development
        
        
        # Set environment variables for the session
        os.environ['STUDENTVUE_USERNAME'] = username
        os.environ['STUDENTVUE_PASSWORD'] = password
        os.environ['STUDENTVUE_DOMAIN'] = 'va-pwcps-psv.edupoint.com'

        # Fetch gradebook
        with st.spinner('Fetching your grades...'):
            gradebook = fetch_gradebook()

        if not gradebook or 'Gradebook' not in gradebook:
            st.error("No gradebook data available. Please check your credentials.")
            return

        # Display courses
        courses_data = gradebook['Gradebook'].get('Courses', {})
        if not isinstance(courses_data, dict):
            st.error("Invalid gradebook format")
            return
                
        courses = courses_data.get('Course', [])
        if not isinstance(courses, list):
            courses = [courses]

        for course in courses:
            if not isinstance(course, dict):
                continue
                    
            course_title = course.get('@Title', 'N/A')
            period = course.get('@Period', 'N/A')
            
            # Handle period number extraction for both string and integer values
            if isinstance(period, int):
                period_num = str(period)
            else:
                period_num = ''.join(filter(str.isdigit, str(period)))
            
            # Create course card
            st.markdown(f'<div class="course-card">', unsafe_allow_html=True)
            
            # Course header
            st.subheader(f"{period_num} - {course_title}")
            
            # Get marks/grades
            marks_data = course.get('Marks', {})
            if isinstance(marks_data, dict):
                marks = marks_data.get('Mark', [])
                if not isinstance(marks, list):
                    marks = [marks]
                
                # Filter out semester grades and sort by marking period
                quarter_marks = []
                for mark in marks:
                    if isinstance(mark, dict) and mark.get('@MarkName', '').startswith('HS-MK'):
                        quarter_marks.append(mark)
                
                quarter_marks.sort(key=lambda x: x.get('@MarkName', ''))
                
                if quarter_marks:
                    # Display grades in columns
                    st.markdown('<div class="grade-section">', unsafe_allow_html=True)
                    grade_cols = st.columns(len(quarter_marks))
                    for idx, mark in enumerate(quarter_marks):
                        with grade_cols[idx]:
                            calculated_score = mark.get('@CalculatedScoreString', 'N/A')
                            raw_score = mark.get('@CalculatedScoreRaw', 'N/A')
                            mark_name = mark.get('@MarkName', '')
                            quarter_num = mark_name[-1] if mark_name else str(idx + 1)
                            
                            st.metric(
                                label=f"Q{quarter_num}",
                                value=f"{calculated_score}",
                                delta=f"{raw_score}%"
                            )
                    st.markdown('</div>', unsafe_allow_html=True)

            # Display assignments
            assignments_data = course.get('Assignments', {})
            if isinstance(assignments_data, dict):
                assignments = assignments_data.get('Assignment', [])
                if not isinstance(assignments, list):
                    assignments = [assignments]

                if assignments:
                    st.markdown('<div class="assignment-section">', unsafe_allow_html=True)
                    st.markdown("### Assignments")
                    for assignment in assignments:
                        if isinstance(assignment, dict):
                            st.markdown('<hr>', unsafe_allow_html=True)
                            st.write(f"**{assignment.get('@Measure', 'N/A')}** - {assignment.get('@Type', 'N/A')}")
                            st.write(f"Date: {assignment.get('@Date', 'N/A')}")
                            st.write(f"Due Date: {assignment.get('@DueDate', 'N/A')}")
                            st.write(f"Score: {assignment.get('@DisplayScore', 'N/A')}")
                            if assignment.get('@Notes'):
                                st.write(f"Notes: {assignment.get('@Notes')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("Error fetching gradebook. Please try again later.")

if __name__ == "__main__":
    main() 