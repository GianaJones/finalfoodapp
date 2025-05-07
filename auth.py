import streamlit as st
import requests

def google_login():
    """Manual OAuth login with a working Google Auth URL."""
    CLIENT_ID = st.secrets["google"]["client_id"]
    REDIRECT_URI = st.secrets["google"]["redirect_uri"]
    SCOPE = "openid email profile"
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

    params = st.query_params

    # Step 1: Handle callback
    if "code" in params and "state" in params and "access_token" not in st.session_state:
        code = params["code"]

        try:
            response = requests.post(
                TOKEN_ENDPOINT,
                data={
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": st.secrets["google"]["client_secret"],
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            token = response.json()
            st.session_state["access_token"] = token["access_token"]
            st.query_params.clear()
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.query_params.clear()
            return False

    # Step 2: Show login button with working link
    if "access_token" not in st.session_state:
        auth_url = (
            f"{AUTH_ENDPOINT}?"
            f"client_id={CLIENT_ID}&"
            f"redirect_uri={REDIRECT_URI}&"
            f"response_type=code&"
            f"scope={SCOPE.replace(' ', '%20')}&"
            f"access_type=offline&"
            f"prompt=consent&"
            f"state=streamlit_login"
        )

        #st.write(auth_url)
        st.sidebar.markdown(
        f'<a href="{auth_url}" target="_blank">🔐 Login with Google</a>',
        unsafe_allow_html=True
        )

    return True

# Code is from ChatGPT

def get_google_user_info():
    """Fetch the authenticated user's full name (first and last) and email using the access token"""
    access_token = st.session_state.get("access_token")

    if access_token:
        # Set the Authorization header with the access token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Use Google People API to fetch user info (including first and last names)
        user_info_url = "https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses"
        response = requests.get(user_info_url, headers=headers)

        if response.status_code == 200:
            user_data = response.json()

            # Extracting first name, last name, and email
            first_name = user_data['names'][0].get('givenName')
            last_name = user_data['names'][0].get('familyName')
            email = user_data['emailAddresses'][0].get('value')

            return first_name, last_name, email
        else:
            st.error(f"Failed to fetch user info: {response.text}")
            return None, None, None
    else:
        st.error("Sign in first!")
        return None, None, None

# Example usage:
first_name, last_name, email = get_google_user_info()

if first_name and last_name and email:
    st.write(f"User's Full Name: {first_name} {last_name}")
    st.write(f"User's Google Email: {email}")
else:
    st.error("Could not retrieve user information from Google.")
