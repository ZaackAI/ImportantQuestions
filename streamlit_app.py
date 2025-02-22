import datetime
import random
import pandas as pd
import streamlit as st

# Show app title and description
st.set_page_config(page_title="Important Questions", page_icon="📚", layout="wide")
st.title("📚 Important Questions")
st.write(
    """
    Welcome to the *Important Questions* app! Share and discover questions from past exams to identify patterns 
    and prepare better for upcoming exams. Add questions you encountered, and the app will automatically predict 
    how many times they have appeared in past papers.
    """
)

# Define subjects list at global scope (reduced to 4 core subjects)
subjects = ["Mathematics", "Physics", "Chemistry", "Biology"]

# Create subject-specific question banks
subject_questions = {
    "Mathematics": [
        "Derive the quadratic formula and explain its components",
        "Solve a system of linear equations using matrices",
        "Explain the concept of differentiation and its applications",
        "Prove the Pythagorean theorem",
        "Solve problems involving trigonometric functions",
        "Explain the concept of integration and its real-world applications",
        "Solve problems involving complex numbers",
        "Explain the binomial theorem and its applications"
    ],
    "Physics": [
        "Explain Newton's laws of motion with practical examples",
        "Describe the principles of electromagnetic induction",
        "Explain the concept of wave-particle duality",
        "Describe the working principle of a nuclear reactor",
        "Explain the laws of thermodynamics",
        "Describe the principles of quantum mechanics",
        "Explain the concept of gravitational fields",
        "Describe the physics behind semiconductors"
    ],
    "Chemistry": [
        "Explain the periodic trends in atomic properties",
        "Describe the mechanism of organic reactions",
        "Explain the concept of chemical equilibrium",
        "Describe the properties of transition elements",
        "Explain the principles of electrochemistry",
        "Describe the structure and properties of polymers",
        "Explain the concepts of acid-base equilibria",
        "Describe the principles of chemical kinetics"
    ],
    "Biology": [
        "Explain the process of photosynthesis in detail",
        "Describe the structure and function of DNA",
        "Explain the process of cellular respiration",
        "Describe the human digestive system",
        "Explain the principles of genetic inheritance",
        "Describe the process of protein synthesis",
        "Explain the immune system's response to infection",
        "Describe the process of evolution and natural selection"
    ]
}

# Create a random Pandas dataframe with existing questions
if "df" not in st.session_state:
    # Set seed for reproducibility
    random.seed(42)
    
    data = []
    question_id = 1100
    
    for subject, questions in subject_questions.items():
        for question in questions:
            # Add 2-3 variations of each question with different marks
            num_variations = random.randint(2, 3)
            for _ in range(num_variations):
                # Simulate historical years the question appeared
                years_appeared = random.sample(range(2018, 2024), random.randint(1, 5))  # Random years between 2018 and 2023
                data.append({
                    "ID": f"Q{question_id}",
                    "Question": question,
                    "Subject": subject,
                    "Status": random.choice(["Verified", "Pending", "Featured"]),
                    "Marks": random.choice([2.5, 5, 10]),
                    "Frequency": len(years_appeared),  # Frequency is the number of years it appeared
                    "Years Appeared": years_appeared  # Store the actual years the question appeared
                })
                question_id -= 1
    
    df = pd.DataFrame(data)
    # Sort initially by Subject and Frequency
    df = df.sort_values(by=['Subject', 'Frequency'], ascending=[True, False])
    st.session_state.df = df

# Function to predict how many times a question has appeared in the past X years
def predict_appearances(question, years):
    # Check if the question exists in the dataframe
    matches = st.session_state.df[st.session_state.df.Question == question]
    if len(matches) == 0:
        return 0  # Question not found
    else:
        # Get the years the question appeared
        years_appeared = matches.iloc[0].get("Years Appeared", [])
        # Count how many times it appeared in the last X years
        current_year = datetime.datetime.now().year
        return sum(1 for year in years_appeared if current_year - year <= years)

# Sidebar for logo and additional info
with st.sidebar:
    # Add text-based logo at the top of the sidebar
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>CTRL+ALT+DEFEAT</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("📝 Add a New Question")
    with st.form("add_question_form"):
        subject = st.selectbox("Subject", sorted(subjects))
        question = st.text_area("Enter the question")
        marks = st.selectbox("Marks", [2.5, 5, 10])
        years_appeared = st.multiselect("Years the question appeared", options=range(2018, 2024), default=[2023])
        submitted = st.form_submit_button("Submit Question")

    if submitted:
        # Add new question to the dataframe
        recent_question_number = int(max(st.session_state.df.ID).replace('Q', ''))
        today = datetime.datetime.now().date()
        df_new = pd.DataFrame(
            [
                {
                    "ID": f"Q{recent_question_number+1}",
                    "Question": question,
                    "Subject": subject,
                    "Status": "Pending",
                    "Marks": marks,
                    "Frequency": len(years_appeared),
                    "Years Appeared": years_appeared
                }
            ]
        )

        st.success("Question submitted successfully!")
        # Concatenate and sort the dataframe
        st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)
        st.session_state.df = st.session_state.df.sort_values(by=['Subject', 'Frequency'], ascending=[True, False])

# Main content
st.header("📂 Question Bank")

# Add subject filter above the table
selected_subject = st.selectbox(
    "Filter by Subject",
    ["All Subjects"] + sorted(subjects),
    key="subject_filter"
)

# Filter dataframe based on selected subject and sort by frequency
if selected_subject != "All Subjects":
    filtered_df = st.session_state.df[st.session_state.df.Subject == selected_subject].copy()
    filtered_df = filtered_df.sort_values('Frequency', ascending=False)
else:
    filtered_df = st.session_state.df.copy()
    filtered_df = filtered_df.sort_values(by=['Subject', 'Frequency'], ascending=[True, False])

st.write(f"Total questions available for {selected_subject}: {len(filtered_df)}")

# Show the questions dataframe with edit capability
edited_df = st.data_editor(
    filtered_df[['ID', 'Question', 'Subject', 'Status', 'Marks', 'Frequency', 'Years Appeared']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Question status",
            options=["Verified", "Pending", "Featured"],
            required=True,
        ),
        "Subject": st.column_config.SelectboxColumn(
            "Subject",
            help="Subject",
            options=sorted(subjects),
            required=True,
        ),
        "Marks": st.column_config.SelectboxColumn(
            "Marks",
            help="Question marks",
            options=[2.5, 5, 10],
            required=True,
        ),
        "Frequency": st.column_config.NumberColumn(
            "Frequency",
            help="Number of times this question appeared",
            min_value=1,
            max_value=100,
        ),
        "Years Appeared": st.column_config.ListColumn(
            "Years Appeared",
            help="Years the question appeared in past papers",
        ),
    },
    disabled=["ID"],
)

# Statistics section
st.header("📊 Analysis")

# Show metrics for filtered data
col1, col2 = st.columns(2)
num_featured = len(filtered_df[filtered_df.Status == "Featured"])
high_freq_questions = len(filtered_df[filtered_df.Frequency >= 5])
col1.metric(label="Featured Questions", value=num_featured)
col2.metric(label="Highly Repeated Questions", value=high_freq_questions)

# Display Highly Repeated Questions in a table
st.write("##### Highly Repeated Questions")
high_freq_table = filtered_df[filtered_df.Frequency >= 5][['Question', 'Subject', 'Marks', 'Frequency', 'Years Appeared']]
st.dataframe(high_freq_table, use_container_width=True, hide_index=True)

# Prediction Section
st.header("🔮 Prediction")

# Input for prediction
question_to_predict = st.text_input("Enter a question to predict its past appearances:")
years_to_predict = st.selectbox("Select time period for prediction", [5, 10, 15], key="years_to_predict")

if question_to_predict:
    # Predict appearances
    appearances = predict_appearances(question_to_predict, years_to_predict)
    st.write(f"The question '{question_to_predict}' has appeared {appearances} times in the past {years_to_predict} years.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p>📧 Contact us: <a href="mailto:support@importantquestions.com">support@importantquestions.com</a></p>
        <p>Follow us:</p>
        <p>
            <a href="https://facebook.com" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" width="30">
            </a>
            <a href="https://instagram.com" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="30">
            </a>
            <a href="https://linkedin.com" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30">
            </a>
        </p>
        <p>© 2023 Important Questions. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
