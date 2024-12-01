import streamlit as st
from PIL import Image
from auth import show_registration_page, show_login_page
from database import add_patient, get_all_patients, get_patient_by_id
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Load the pre-trained model
model = load_model('model/model_cnn.h5')

def glaucoma_prediction(test_image):
    image = img_to_array(test_image)
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    result = np.argmax(predictions)
    return result, predictions

# Main application
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    option = st.sidebar.selectbox("Select Option", ["Login", "Register"])
    if option == "Register":
        show_registration_page()
    elif option == "Login":
        st.session_state.logged_in = show_login_page()
else:
    # Display logged-in user's username
    st.sidebar.markdown(f"<span>Hello, </span><span style='color: red;'>@{st.session_state.username}</span>", unsafe_allow_html=True)

    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    st.title("Glaucoma Detection App")
    
    option = st.sidebar.selectbox("Select Option", ["Detect Glaucoma", "View Patients"])

    if option == "Detect Glaucoma":
        uploaded_image = st.file_uploader("Choose a Fundus image...", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            test_image = image.resize((256, 256))

            prediction, predictions = glaucoma_prediction(test_image)

            diagnosis = "Glaucoma" if prediction == 0 else "Not Glaucoma"
            st.write(f"**Prediction: {diagnosis}**")

            confidence = predictions[0][prediction] * 100
            st.write(f"Confidence: {confidence:.2f}%")

            # Plot confidence bar chart
            fig, ax = plt.subplots()
            labels = ["Glaucoma", "Not Glaucoma"]
            ax.bar(labels, predictions[0] * 100)
            ax.set_ylabel("Confidence (%)")
            st.pyplot(fig)

            # Patient form
            first_name = st.text_input("First Name", placeholder="Enter your first name...")
            last_name = st.text_input("Last Name", placeholder="Enter your last name...")
            age = st.number_input("Age", min_value=0)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            email = st.text_input("Email (Optional)")
            phone = st.text_input("Phone", placeholder="Enter with Country code (e.g +234)")
            notes = st.text_area("Notes", placeholder="Describe the patient's condition here/input Confidence")
            
            if st.button("Add Patient"):
                date_of_diagnosis = datetime.datetime.now()  # Updated to current datetime
                add_patient(first_name, last_name, age, gender, diagnosis, date_of_diagnosis, email, phone, notes, st.session_state.doctor_id)
                st.success("Patient added successfully")

    elif option == "View Patients":
        st.subheader("All Patients")

        # Search functionality
        search_query = st.text_input("Search for a patient by name or ID", "")
        
        # Date filters: "Today", "Yesterday", "Custom Date", "All", "Date Range"
        date_filter = st.selectbox("Filter by Date", ["All", "Today", "Yesterday", "Custom Date", "Date Range"])

        today = datetime.datetime.now()
        selected_date = None

        # Filter logic based on the date filter
        if date_filter == "Today":
            selected_date = today.date()
        elif date_filter == "Yesterday":
            selected_date = (today - datetime.timedelta(days=1)).date()
        elif date_filter == "Custom Date":
            selected_date = st.date_input("Select a date", value=today.date())

        # Initialize empty variables for custom date range
        start_date = None
        end_date = None

        # Show custom date range inputs if "Date Range" is selected
        if date_filter == "Date Range":
            start_date = st.date_input("Start Date", value=today.date())
            end_date = st.date_input("End Date", value=today.date())

        patients = get_all_patients(st.session_state.doctor_id)  # Fetch all patients created by this doctor
        
        # Filter by search query
        if search_query:
            patients = [patient for patient in patients 
                        if search_query.lower() in patient[1].lower() or 
                           search_query.lower() in patient[2].lower() or 
                           search_query in str(patient[0])]

        # Filter by specific date (fix applied)
        if selected_date:
           patients = [patient for patient in patients 
                       if datetime.datetime.fromisoformat(patient[6]).date() == selected_date]

        # Filter by date range
        if date_filter == "Date Range" and start_date and end_date:
            patients = [patient for patient in patients 
                        if start_date <= datetime.datetime.fromisoformat(patient[6]).date() <= end_date]

        # Sort patients by date of diagnosis (assuming index 6 is the date)
        patients.sort(key=lambda x: datetime.datetime.fromisoformat(x[6]), reverse=True)  # Sort in descending order (newest first)

        # Display patients with pagination
        if "offset" not in st.session_state:
            st.session_state.offset = 0
        if "records_per_page" not in st.session_state:
            st.session_state.records_per_page = 20
        
        # Display the patients based on pagination
        displayed_patients = patients[st.session_state.offset:st.session_state.offset + st.session_state.records_per_page]
        
        for patient in displayed_patients:
            if st.button(f'View {patient[1].capitalize()} {patient[2].capitalize()}', key=f'view_patient_{patient[0]}'):
                patient_data = get_patient_by_id(patient[0])
                
                patient_data = {
                    'Id': patient_data[0],
                    'First Name': patient_data[1],
                    'Last Name': patient_data[2],
                    'Age': patient_data[3],
                    'Gender': patient_data[4],
                    'Diagnosis': patient_data[5],
                    'Date': patient_data[6],
                    'Email': patient_data[7],
                    'Phone': patient_data[8],
                    'Doctors Notes': patient_data[9]
                }

                # Create an expander to show patient details
                with st.expander("View Patient Details", expanded=False):
                    st.markdown(f"<p><strong>First Name:</strong> {patient_data['First Name']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Last Name:</strong> {patient_data['Last Name']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Age:</strong> {patient_data['Age']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Gender:</strong> {patient_data['Gender']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Diagnosis:</strong> {patient_data['Diagnosis']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Date:</strong> {patient_data['Date']}</p>", unsafe_allow_html=True)
                    if patient_data['Email']:
                        st.markdown(f"<p><strong>Email:</strong> {patient_data['Email']}</p>", unsafe_allow_html=True)
                    if patient_data['Phone']:
                        st.markdown(f"<p><strong>Phone:</strong> {patient_data['Phone']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Doctor's Notes:</strong> {patient_data['Doctors Notes']}</p>", unsafe_allow_html=True)

        # "See More" Button
        if st.session_state.offset + st.session_state.records_per_page < len(patients):
            if st.button("See More"):
                st.success('Opening Latest records...')
                st.session_state.offset += st.session_state.records_per_page 
                st.rerun()  # Rerun the script to refresh the displayed records
        elif st.session_state.offset > 0:
            if st.button("Previous"):
                st.success('Opening Previous records...')
                st.session_state.offset -= st.session_state.records_per_page
                st.rerun()  # Rerun the script to refresh the displayed records