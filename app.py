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

# Load the CSV file
filename = "NUNSA Election Form (Responses).csv"  # Replace with the correct file path
if os.path.exists(filename):
    df = pd.read_csv(filename)

    # Strip white spaces and standardize column names
    df['First_Name'] = df['First_Name'].str.strip().str.upper()
    df['Middle_Name'] = df['Middle_Name'].str.strip().str.upper()
    df['Last_Name'] = df['Last_Name'].str.strip().str.upper()
    df['Matric_number'] = df['Matric_number'].astype(str).str.strip()
    df['Email_address'] = df['Email_address'].str.strip()
    df['Level'] = df['Level'].str.strip()
else:
    st.error("CSV file not found. Make sure it's in the specified directory.")
    st.stop()

# Check if 'Passkey' column exists, create it if not
if 'Passkey' not in df.columns:
    df['Passkey'] = df.apply(
        lambda row: generate_password(row['Matric_number'], row['Last_Name']), axis=1
    )
    # Save the updated data back to the CSV to ensure consistency
    df.to_csv(filename, index=False)

# Prompt user for their details
first_name = st.text_input("Enter your First Name: ").strip().upper()
middle_name = st.text_input("Enter your Middle Name: ").strip().upper()
last_name = st.text_input("Enter your Last Name: ").strip().upper()
matric_number = st.text_input("Enter your Matric Number: ").strip()
email_registration = st.text_input("Enter your Email Address for Registration: ").strip()  # Unique label
level = st.text_input("Enter your Level (e.g., 100L, 200L): ").strip()

# Add a "SUBMIT" button to submit the form
if st.button("SUBMIT"):
    # Use df.query to check if the user exists in the dataset
    query_str = f"First_Name == '{first_name}' and Middle_Name == '{middle_name}' and Last_Name == '{last_name}' and Matric_number == '{matric_number}' and Email_address == '{email_registration}' and Level == '{level}'"
    matching_user = df.query(query_str)

    if not matching_user.empty:
        # User exists, retrieve the Passkey
        passkey = matching_user.iloc[0]['Passkey']
        if pd.notna(passkey):
            st.success(f"Hello {first_name}, your Passkey is: {passkey}")
        else:
            st.warning(f"Hello {first_name}, no Passkey found in the dataset.")
    else:
        st.error("No matching record found. Please verify your details and try again. You may not be registered, try registering here https://docs.google.com/forms/d/e/1FAIpQLSdriD-bmBB3lkhwvM198t0Fu-SZpK1GRIacqEeC6gUyWFsvZg/viewform?usp=sf_link")

# Check if the email is authorized to download the CSV
authorized_emails = ["owhorodesuccess95@gmail.com", "nunsacmul22@gmail.com"]
if email_registration in authorized_emails:
    email_download = st.text_input("Enter your Email Address for CSV Download: ").strip()  # Unique label
    if email_download in authorized_emails:
        # Download button for the updated CSV
        st.download_button(
            label="Download CSV with Passkeys",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="NUNSA_Election_Form_with_Passkeys.csv",
            mime='text/csv',
        )
