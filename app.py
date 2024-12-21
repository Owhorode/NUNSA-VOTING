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
    return hex_dig[:password_length]

# Streamlit app configuration
st.set_page_config(page_title="NUNSA Voters Registration", page_icon="NUNSA.png")

# Layout with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    image = Image.open("NUNSA.png")  # Replace with the path to your image
    st.image(image, caption='NUNSA', use_container_width=False, width=100)
with col2:
    st.title("NUNSA VOTERS REGISTRATION")

# Load the CSV file
filename = "NUNSA_Election_Form_with_Passkeys.csv"  # Replace with the correct file path
if os.path.exists(filename):
    df = pd.read_csv(filename)

    # Strip white spaces from all column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    # Standardize values in the relevant columns
    for column in ['first_name', 'middle_name', 'last_name', 'matric_number', 'email_address', 'level']:
        if column in df.columns:
            df[column] = df[column].str.strip()

    # Check if 'Passkey' column exists, create it if not
    if 'Passkey' not in df.columns:
        df['Passkey'] = df.apply(lambda row: generate_password(row['matric_number'], row['last_name']), axis=1)
        df.to_csv(filename, index=False)  # Save updated data

else:
    st.error("CSV file not found. Make sure it's in the specified directory.")
    st.stop()

# Prompt user for their details
first_name = st.text_input("Enter your First Name: ").strip()
middle_name = st.text_input("Enter your Middle Name: ").strip()
last_name = st.text_input("Enter your Last Name: ").strip()
matric_number = st.text_input("Enter your Matric Number: ").strip()
email_registration = st.text_input("Enter your Email Address for Registration: ").strip()  # Unique label
level = st.text_input("Enter your Level (e.g., 100L, 200L): ").strip()

# Add a "SUBMIT" button to submit the form
if st.button("SUBMIT"):
    # Use df.query to check if the user exists in the dataset
    query_str = f"first_name == '{first_name}' and middle_name == '{middle_name}' and last_name == '{last_name}' and matric_number == '{matric_number}' and email_address == '{email_registration}' and level == '{level}'"
    matching_user = df.query(query_str)

    if not matching_user.empty:
        # User exists, retrieve the Passkey
        passkey = matching_user.iloc[0]['Passkey']
        st.success(f"Hello {first_name}, your Passkey is: {passkey}")
    else:
        st.error("No matching record found. Please verify your details and try again.")

# Check if the email is authorized to download the CSV
authorized_emails = ["owhorodesuccess95@gmail.com", "nunsacmul22@gmail.com"]
if email_registration in authorized_emails:
    email_download = st.text_input("Enter your Email Address for CSV Download: ").strip()
    if email_download in authorized_emails:
        # Download button for the updated CSV
        st.download_button(
            label="Download CSV with Passkeys",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="NUNSA_Election_Form_with_Passkeys.csv",
            mime='text/csv',
        )