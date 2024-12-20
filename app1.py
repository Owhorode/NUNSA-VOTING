import streamlit as st
import pandas as pd
import hashlib
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
st.set_page_config(page_title="NUNSA Passkey Generator", page_icon="NUNSA.png")

# Create a layout with two columns
col1, col2 = st.columns([1, 4])

with col1:
    # Display the NUNSA logo
    image = Image.open("NUNSA.png")  # Replace with the path to your image
    st.image(image, caption='NUNSA', use_container_width=False, width=100)

with col2:
    # Title
    st.title("NUNSA PASSKEY GENERATOR")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    data = pd.read_csv(uploaded_file)

    # Strip white spaces and standardize column names
    data['First_Name'] = data['First_Name'].str.strip().str.upper()
    data['Middle_Name'] = data['Middle_Name'].str.strip().str.upper()
    data['Last_Name'] = data['Last_Name'].str.strip().str.upper()
    data['Matric_number'] = data['Matric_number'].astype(str).str.strip()
    data['Email_address'] = data['Email_address'].str.strip()
    data['Level'] = data['Level'].str.strip()

    # Generate passkeys
    data['Passkey'] = data.apply(lambda row: generate_password(row['Matric_number'], row['Last_Name']), axis=1)

    # Display the updated data
    st.write(data)

    # Provide a download button for the updated CSV file
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV with Passkeys",
        data=csv,
        file_name="NUNSA_Election_Form_with_Passkeys.csv",
        mime='text/csv',
    )
