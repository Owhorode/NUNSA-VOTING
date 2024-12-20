import streamlit as st
import pandas as pd
import hashlib
import re
import os
from PIL import Image

# Function to generate a deterministic password
def generate_password(matric_number, last_name):
    merge = str(matric_number) + last_name.lower()
    hash_object = hashlib.sha256(merge.encode())
    hex_dig = hash_object.hexdigest()
    password_length = min(12, len(hex_dig))  # Ensure the password is not longer than 'merge'
    password = hex_dig[:password_length]
    return password

# Function to validate user input
def validate_input(first_name, middle_name, last_name, matric_number, email):
    if len(matric_number) != 9:
        return "Incorrect Matric Number"
    if len(first_name) < 3:
        return "Incorrect First Name"
    if len(middle_name) < 3:
        return "Incorrect Middle Name"
    if len(last_name) < 3:
        return "Incorrect Last Name"
    return None

# Function to validate level input
def validate_level(level):
    # Check if the level matches the pattern (e.g., 100L, 200L, etc.)
    if re.match(r'^\d{3}L$', level):
        return None
    return "Incorrect Input"

# Streamlit app
st.set_page_config(page_title="NUNSA Voters Registration", page_icon="NUNSA.png")

# Create a layout with two columns
col1, col2 = st.columns([1, 4])

with col1:
    # Display the NUNSA logo
    image = Image.open("NUNSA.png")  # Replace with the path to your image
    st.image(image, caption='NUNSA', use_container_width=False, width=100)

with col2:
    # Title
    st.title("NUNSA VOTERS REGISTRATION")

# Load the existing CSV file
csv_file = "NUNSA Election Form (Responses).csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    # Generate passkeys for all existing users
    if 'Passkey' not in df.columns:
        df['Passkey'] = df.apply(
            lambda row: generate_password(row['Matric_number'], row['Last_Name']), axis=1
        )
else:
    df = pd.DataFrame(columns=['Timestamp', 'First_Name', 'Middle_Name', 'Last_Name', 'Matric_number', 'Email_address', 'Level', 'Passkey'])

# Convert names to uppercase
df['First_Name'] = df['First_Name'].str.upper()
df['Middle_Name'] = df['Middle_Name'].str.upper()
df['Last_Name'] = df['Last_Name'].str.upper()

# Initialize the attempt counter
attempts = 0
max_attempts = 3

# Use session state to keep track of attempts
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0

# Prompt user for their details
first_name = st.text_input("Enter your First Name: ").strip().upper()
middle_name = st.text_input("Enter your Middle Name: ").strip().upper()
last_name = st.text_input("Enter your Last Name: ").strip().upper()
matric_number = st.text_input("Enter your Matric Number: ").strip()
email = st.text_input("Enter your Email Address: ").strip()
level = st.text_input("Enter your Level (e.g., 100L, 200L): ").strip()

# Validate user input only if the fields are not empty
if first_name and middle_name and last_name and matric_number and email:
    validation_error = validate_input(first_name, middle_name, last_name, matric_number, email)
    if validation_error:
        st.error(validation_error)
        st.session_state.attempts += 1
    else:
        level_error = validate_level(level)
        if level_error:
            st.error(level_error)
            st.session_state.attempts += 1
        else:
            # Check if the user exists in the dataset
            existing_user = df[
                (df['First_Name'] == first_name) &
                (df['Middle_Name'] == middle_name) &
                (df['Last_Name'] == last_name) &
                (df['Matric_number'] == matric_number) &
                (df['Email_address'] == email)
            ]

            if not existing_user.empty:
                # User exists
                passkey = existing_user.iloc[0]['Passkey']
                st.success(f"Hello {first_name}, you have already registered! Your passkey is: {passkey}.")
            else:
                # User is not in the dataset, register them
                passkey = generate_password(matric_number, last_name)
                new_entry = {
                    'Timestamp': pd.Timestamp.now(),
                    'First_Name': first_name,
                    'Middle_Name': middle_name,
                    'Last_Name': last_name,
                    'Matric_number': matric_number,
                    'Email_address': email,
                    'Level': level,  # Add the provided level
                    'Passkey': passkey
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                st.markdown(f"Hello {first_name}, you have been registered, your passkey is: <span style='font-size:2em;'>{passkey}</span>.", unsafe_allow_html=True)

if st.session_state.attempts == max_attempts:
    st.error("You have been blocked, please send a complaint to nunsacmul22@gmail.com")

# Save the updated data back to the CSV
df.to_csv(csv_file, index=False)

# Check if the email is authorized to download the CSV
authorized_emails = ["owhorodesuccess95@gmail.com", "nunsacmul22@gmail.com"]
if email in authorized_emails:
    # Download button for the updated CSV
    st.download_button(
        label="Download CSV with Passkeys",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="NUNSA_Election_Form_with_Passkeys.csv",
        mime='text/csv',
    )
