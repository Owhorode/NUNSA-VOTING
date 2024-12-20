import streamlit as st
import pandas as pd
import hashlib
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

# Load the existing CSV file and generate passkeys for all existing users
csv_file = "NUNSA Election Form (Responses).csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    # Generate passkeys for all existing users
    if 'Passkey' not in df.columns:
        df['Passkey'] = df.apply(
            lambda row: generate_password(row['Matric_number'], row['Last_Name']), axis=1
        )
else:
    st.error("CSV file not found. Please ensure the file is in the current directory.")
    st.stop()

# Convert names to uppercase
df['First_Name'] = df['First_Name'].str.upper()
df['Middle_Name'] = df['Middle_Name'].str.upper()
df['Last_Name'] = df['Last_Name'].str.upper()

# Prompt user for their details
first_name = st.text_input("Enter your First Name: ").strip().upper()
middle_name = st.text_input("Enter your Middle Name: ").strip().upper()
last_name = st.text_input("Enter your Last Name: ").strip().upper()
matric_number = st.text_input("Enter your Matric Number: ").strip()

# Add an "OK" button to submit the form
if st.button("SUBMIT"):
    # Check if the user exists in the dataset
    existing_user = df[
        (df['Last_Name'] == last_name) &
        (df['Matric_number'] == matric_number)
    ]

    if not existing_user.empty:
        # User exists
        passkey = existing_user.iloc[0]['Passkey']
        st.success(f"Hello {first_name}, your passkey is: {passkey}.")
    else:
        # User is not in the dataset
        st.error("You did not register for this election. Please send a mail to nunsacmul22@gmail.com.")

# Check if the email is authorized to download the CSV
authorized_emails = ["owhorodesuccess95@gmail.com", "nunsacmul22@gmail.com"]
email = st.text_input("Enter your Email Address: ").strip()
if email in authorized_emails:
    # Download button for the updated CSV
    st.download_button(
        label="Download CSV with Passkeys",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="NUNSA_Election_Form_with_Passkeys.csv",
        mime='text/csv',
    )
