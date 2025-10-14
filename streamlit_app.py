import streamlit as st
import pandas as pd
import requests
import io

st.title("Network Security Phishing Detection")
st.write("Upload a CSV file to detect phishing URLs")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Display uploaded data preview
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())
    
    if st.button("Predict"):
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Send to FastAPI backend
            files = {"file": ("data.csv", uploaded_file, "text/csv")}
            response = requests.post("http://localhost:8000/predict", files=files)
            
            if response.status_code == 200:
                # Parse HTML response and extract table
                html_content = response.text
                
                # Check if output file exists
                import os
                if os.path.exists("prediction_output/output.csv"):
                    # Read the saved output file
                    result_df = pd.read_csv("prediction_output/output.csv", index_col=0)
                    
                    st.subheader("Prediction Results")
                    st.dataframe(result_df)
                    
                    # Show summary
                    phishing_count = (result_df['predicted_column'] == 1).sum()
                    safe_count = (result_df['predicted_column'] == 0).sum()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Phishing URLs", phishing_count)
                    with col2:
                        st.metric("Safe URLs", safe_count)
                else:
                    st.error("Output file not found. Please check the FastAPI server.")
                    
            else:
                st.error(f"Prediction failed: {response.status_code}")
                st.error(f"Response: {response.text}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure the FastAPI server is running on http://localhost:8000")