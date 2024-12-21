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

# Upload file (CSV or Excel)
uploaded_file = st.file_uploader("Upload your file (CSV or Excel)", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Detect file type and load data
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(uploaded_file)  # Requires openpyxl for .xlsx files

        # Standardize column names (remove spaces, make lowercase, and handle other formats)
        data.columns = data.columns.str.strip().str.replace(" ", "_").str.lower()

        # Check for required columns
        required_columns = ['first_name', 'middle_name', 'last_name', 'matric_number', 'email_address', 'level']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"The uploaded file is missing the following required columns: {', '.join(missing_columns)}")
        else:
            # Standardize values
            data['first_name'] = data['first_name'].str.strip().str.upper()
            data['middle_name'] = data['middle_name'].str.strip().str.upper()
            data['last_name'] = data['last_name'].str.strip().str.upper()
            data['matric_number'] = data['matric_number'].astype(str).str.strip()
            data['email_address'] = data['email_address'].str.strip()
            data['level'] = data['level'].str.strip()

            # Generate passkeys
            data['passkey'] = data.apply(lambda row: generate_password(row['matric_number'], row['last_name']), axis=1)

            # Display the updated data
            st.write(data)

            # Provide a download button for the updated file
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV with Passkeys",
                data=csv,
                file_name="NUNSA_Election_Form_with_Passkeys.csv",
                mime='text/csv',
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")