import streamlit as st
import pandas as pd
import requests
import io
import os

# API Configuration - use environment variable for production
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Network Security Phishing Detection")
st.write("Detect phishing URLs using CSV upload or single URL input")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["CSV Upload", "Single URL"])

with tab1:
    st.write("Upload a CSV file to detect multiple phishing URLs")
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

with tab2:
    st.write("Enter URL features for single prediction")
    
    # Single URL input form
    with st.form("url_form"):
        st.subheader("URL Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            having_IP_Address = st.selectbox("Having IP Address", [-1, 1], help="-1: No, 1: Yes")
            URL_Length = st.selectbox("URL Length", [-1, 0, 1], help="-1: Short, 0: Medium, 1: Long")
            Shortining_Service = st.selectbox("Shortening Service", [-1, 1], help="-1: No, 1: Yes")
            having_At_Symbol = st.selectbox("Having @ Symbol", [-1, 1], help="-1: No, 1: Yes")
            double_slash_redirecting = st.selectbox("Double Slash Redirecting", [-1, 1], help="-1: No, 1: Yes")
            Prefix_Suffix = st.selectbox("Prefix Suffix", [-1, 1], help="-1: No, 1: Yes")
            having_Sub_Domain = st.selectbox("Having Sub Domain", [-1, 0, 1], help="-1: No, 0: One, 1: Multiple")
            SSLfinal_State = st.selectbox("SSL Final State", [-1, 0, 1], help="-1: No SSL, 0: Trusted, 1: Untrusted")
            Domain_registeration_length = st.selectbox("Domain Registration Length", [-1, 1], help="-1: Short, 1: Long")
            Favicon = st.selectbox("Favicon", [-1, 1], help="-1: External, 1: Internal")
            port = st.selectbox("Port", [-1, 1], help="-1: Closed, 1: Open")
            HTTPS_token = st.selectbox("HTTPS Token", [-1, 1], help="-1: No, 1: Yes")
            Request_URL = st.selectbox("Request URL", [-1, 0, 1], help="-1: <22%, 0: 22-61%, 1: >61%")
            URL_of_Anchor = st.selectbox("URL of Anchor", [-1, 0, 1], help="-1: <31%, 0: 31-67%, 1: >67%")
            Links_in_tags = st.selectbox("Links in Tags", [-1, 0, 1], help="-1: <17%, 0: 17-81%, 1: >81%")
        
        with col2:
            SFH = st.selectbox("SFH", [-1, 0, 1], help="Server Form Handler")
            Submitting_to_email = st.selectbox("Submitting to Email", [-1, 1], help="-1: No, 1: Yes")
            Abnormal_URL = st.selectbox("Abnormal URL", [-1, 1], help="-1: No, 1: Yes")
            Redirect = st.selectbox("Redirect", [-1, 0, 1], help="Number of redirects")
            on_mouseover = st.selectbox("On Mouseover", [-1, 1], help="-1: No, 1: Yes")
            RightClick = st.selectbox("Right Click", [-1, 1], help="-1: Enabled, 1: Disabled")
            popUpWidnow = st.selectbox("Pop Up Window", [-1, 1], help="-1: No, 1: Yes")
            Iframe = st.selectbox("Iframe", [-1, 1], help="-1: No, 1: Yes")
            age_of_domain = st.selectbox("Age of Domain", [-1, 1], help="-1: <6 months, 1: >6 months")
            DNSRecord = st.selectbox("DNS Record", [-1, 1], help="-1: No record, 1: Has record")
            web_traffic = st.selectbox("Web Traffic", [-1, 0, 1], help="-1: Low, 0: Medium, 1: High")
            Page_Rank = st.selectbox("Page Rank", [-1, 1], help="-1: Low, 1: High")
            Google_Index = st.selectbox("Google Index", [-1, 1], help="-1: Not indexed, 1: Indexed")
            Links_pointing_to_page = st.selectbox("Links Pointing to Page", [-1, 0, 1], help="-1: <2, 0: 2-5, 1: >5")
            Statistical_report = st.selectbox("Statistical Report", [-1, 1], help="-1: Safe, 1: Phishing")
        
        submitted = st.form_submit_button("Predict Single URL")
        
        if submitted:
            try:
                # Prepare features array
                features = [
                    having_IP_Address, URL_Length, Shortining_Service, having_At_Symbol,
                    double_slash_redirecting, Prefix_Suffix, having_Sub_Domain, SSLfinal_State,
                    Domain_registeration_length, Favicon, port, HTTPS_token, Request_URL,
                    URL_of_Anchor, Links_in_tags, SFH, Submitting_to_email, Abnormal_URL,
                    Redirect, on_mouseover, RightClick, popUpWidnow, Iframe, age_of_domain,
                    DNSRecord, web_traffic, Page_Rank, Google_Index, Links_pointing_to_page,
                    Statistical_report
                ]
                
                # Send to FastAPI backend
                payload = {"url_features": features}
                response = requests.post(f"{API_URL}/predict_single", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    prediction = result["prediction"]
                    
                    if prediction == "Phishing":
                        st.error(f"🚨 **{prediction}** - This URL appears to be malicious!")
                    else:
                        st.success(f"✅ **{prediction}** - This URL appears to be safe.")
                        
                else:
                    st.error(f"Prediction failed: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info(f"Make sure the FastAPI server is running on {API_URL}")

# CSV Upload functionality
with tab1:

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
                response = requests.post(f"{API_URL}/predict", files=files)
                
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
                st.info(f"Make sure the FastAPI server is running on {API_URL}")