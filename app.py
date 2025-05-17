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
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .grade-breakdown {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📚 StudentVue Gradebook Viewer")
    st.markdown("Enter your StudentVue credentials to view your grades.")

    # Create a form for credentials
    with st.form("login_form"):
        username = st.text_input("Username (email)")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("View Grades")

    if submit_button:
        if not username or not password:
            st.error("Please enter both username and password")
            return

        try:
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
            courses = gradebook['Gradebook'].get('Courses', {}).get('Course', [])
            if not isinstance(courses, list):
                courses = [courses]

            for course in courses:
                with st.container():
                    st.markdown("---")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(course.get('@Title', 'N/A'))
                        st.write(f"Teacher: {course.get('@Teacher', 'N/A')}")
                        st.write(f"Period: {course.get('@Period', 'N/A')}")
                        st.write(f"Room: {course.get('@Room', 'N/A')}")

                    # Get marks/grades
                    marks = course.get('Marks', {}).get('Mark', [])
                    if not isinstance(marks, list):
                        marks = [marks]

                    with col2:
                        for mark in marks:
                            mark_name = mark.get('@MarkName', 'N/A')
                            if mark_name == 'HS-EX2':
                                continue
                                
                            calculated_score = mark.get('@CalculatedScoreString', 'N/A')
                            raw_score = mark.get('@CalculatedScoreRaw', 'N/A')
                            
                            st.metric(
                                label=f"{mark_name} Grade",
                                value=f"{calculated_score}",
                                delta=f"{raw_score}%"
                            )

                    # Show grade breakdown only for current marking period
                    for mark in marks:
                        if mark.get('@MarkName') == 'HS-MK4':
                            grade_calc = mark.get('GradeCalculationSummary', {}).get('AssignmentGradeCalc', [])
                            if not isinstance(grade_calc, list):
                                grade_calc = [grade_calc]

                            st.markdown("### Grade Breakdown")
                            for calc in grade_calc:
                                if calc.get('@Type') != 'TOTAL':
                                    st.progress(
                                        float(calc.get('@WeightedPct', '0').strip('%')) / 100,
                                        text=f"{calc.get('@Type')}: {calc.get('@WeightedPct')} ({calc.get('@CalculatedMark')})"
                                    )

                    # Display recent assignments
                    assignments = course.get('Assignments', {}).get('Assignment', [])
                    if not isinstance(assignments, list):
                        assignments = [assignments]

                    if assignments:
                        st.markdown("### Recent Assignments")
                        for assignment in assignments:
                            with st.expander(f"{assignment.get('@Measure', 'N/A')} - {assignment.get('@Type', 'N/A')}"):
                                st.write(f"Date: {assignment.get('@Date', 'N/A')}")
                                st.write(f"Due Date: {assignment.get('@DueDate', 'N/A')}")
                                st.write(f"Score: {assignment.get('@DisplayScore', 'N/A')}")
                                if assignment.get('@Notes'):
                                    st.write(f"Notes: {assignment.get('@Notes')}")

        except Exception as e:
            st.error(f"Error fetching gradebook: {str(e)}")

if __name__ == "__main__":
    main() 