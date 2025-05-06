
# auth.py
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import requests

def google_login():
    """Don't change this code!"""
    CLIENT_ID = st.secrets["google"]["client_id"]
    CLIENT_SECRET = st.secrets["google"]["client_secret"]
    REDIRECT_URI = st.secrets["google"]["redirect_uri"]

    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    SCOPE = "openid email profile"

    params = st.query_params

    # 🟢 Step 1: Handle Google redirect back with code + state
    if "code" in params and "state" in params and "access_token" not in st.session_state:
        code = params["code"]
        state = params["state"]

        # Restore OAuth session using returned state (from URL)
        oauth = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
            state=state,
        )

        try:
            # Debugging code that Eni used to debug
            #st.write("🔎 Received code:", code)
            #st.write("🔎 Received state:", state)
            #st.write("🔎 Full query params:", st.query_params)
            token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
            st.session_state["access_token"] = token["access_token"]
            st.query_params.clear()
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            #st.write("Query Params on failure:", params)  # 👈 Add this line
            st.query_params.clear()
            return False

    # 👤 Step 2: Not logged in → show login button with state in URL
    if "access_token" not in st.session_state:
        oauth = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
        )
        auth_url, _state = oauth.create_authorization_url(AUTH_ENDPOINT)

        st.sidebar.markdown(
            f"""
            <a href="{auth_url}" target="_self">
                <button style='padding:10px 20px;font-size:16px;background-color:#0b72b9;color:white;border:none;border-radius:5px;cursor:pointer;'>
                    Login with Google
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
        return False

    # ✅ Already logged in
    return True

# Code is from ChatGPT
import requests
import streamlit as st

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
