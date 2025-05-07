import streamlit as st
import pandas as pd
import requests
import json
from datetime import date, timedelta
import random
from auth import get_google_user_info
import sqlite3
import time
#used google gemini for this
# --- Function to fetch a random food fact ---
def get_food_fact():
    api_url = "https://uselessfacts.jsph.pl/random.json?language=en"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        fact = data.get('text', "No food fact available today.")
        # Attempt to filter for food-related facts (this might not be perfect)
        keywords = ["food", "eat", "cook", "ingredient", "fruit", "vegetable", "meat", "dairy", "grain", "spice"]
        if any(keyword in fact.lower() for keyword in keywords):
            return f"Did you know?  {fact}"
        else:
            # If not clearly food-related, try again (you might want to limit retries)
            time.sleep(3)
            return get_food_fact()
    except requests.exceptions.RequestException as e:
        return f"Error fetching food fact: {e}"
    except json.JSONDecodeError:
        return "Error decoding food fact."

# --- Function to store the daily fact in session state ---
def display_daily_food_fact():
    today = date.today()
    fact_key = f"food_fact_{today.strftime('%Y-%m-%d')}"

    if fact_key not in st.session_state:
        st.session_state[fact_key] = get_food_fact()

    st.markdown(
        f"""
        <div style="background-color: rgba(173, 216, 230, 0.5); padding: 10px; border-radius: 5px; font-family: 'Shadows Into Light', cursive !important;">
            <span style="font-size: 1.2em; font-weight: bold; color: #2E8B57;">Food Fact: 💡</span>
            <span style="font-size: 1.1em;">{st.session_state[fact_key]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Display the daily food fact at the top ---
display_daily_food_fact()


st.markdown(
    """
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Shadows+Into+Light&display=swap" rel="stylesheet">
    </head>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
body, h2, h3, h4, h5, h6, p, label, button, div, input, select, option {
    font-family: Arial, sans-serif !important;
}
h1 {
    font-family: 'Shadows Into Light', cursive !important; /* Override Streamlit's style */
}
</style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>
.stApp {
background-color: #A3B18A; 
} </style>
""", unsafe_allow_html=True,
)
st.markdown(
    """
<style>
.stApp {
background-color: #A3B18A; 
}
.stButton button {
background-color: #DAD7CD;}

.stSelectbox > div > div > div {
background-color: #DAD7CD;
}

.stDateInput input {
background-color: #DAD7CD;
}
</style>
""", unsafe_allow_html=True,
)
# Your get_week_menu function
#def get_week_menu(date, locationID, mealID):
    #base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    #params = {"date": date, "locationID": locationID, "mealID": mealID}
    #result = requests.get(base_url, params=params).text
    #data = json.loads(result)
    #return pd.DataFrame(data)
def get_week_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {"date": date, "locationID": locationID, "mealID": mealID}
    result = requests.get(base_url, params=params).text
    data = json.loads(result)
    return pd.DataFrame(data)

st.markdown(
    "<h1 style='font-family: Arial, sans-serif !important;'>Food Tinder - be on the lookout!</h1>",
    unsafe_allow_html=True,
)

# --- Configuration - Choose ONE location and ONE meal to start with ---
default_location_id = '96'  # REPLACE WITH AN ACTUAL LOCATION ID
default_meal_id = '148'      # REPLACE WITH AN ACTUAL MEAL ID

# --- Determine the date for the next week ---
today = date.today()
start_of_next_week = today + timedelta(days=(7 - today.weekday()) % 7 + 7)
next_week_date_str = start_of_next_week.strftime("%Y-%m-%dT00:00:00")

# --- Fetch the menu for the next week for the chosen location and meal ---
weekly_menu_df = get_week_menu(next_week_date_str, default_location_id, default_meal_id)

if 'weekly_menu' not in st.session_state:
    st.session_state['weekly_menu'] = weekly_menu_df.to_dict('records')
if 'current_meal_index' not in st.session_state:
    st.session_state['current_meal_index'] = 0
if 'user_preferences' not in st.session_state:
    st.session_state['user_preferences'] = {}

def record_preference(preference):
    if st.session_state['weekly_menu']:
        meal = st.session_state['weekly_menu'][st.session_state['current_meal_index']]
        meal_name = meal.get('name', 'Unnamed Meal') # Adjust key if needed
        st.session_state['user_preferences'][meal_name] = preference
        if st.session_state['current_meal_index'] < len(st.session_state['weekly_menu']) - 1:
            st.session_state['current_meal_index'] += 1
        else:
            st.info(f"You've seen all the meals for this week at this location and meal!")
    else:
        st.info("No menu data available.")

#Making a list of all of the meals that are already liked in the database
def add_liked_meal(meal):  # 'meal' is the parameter that will receive 'current_meal'
    print(f"add_liked_meal called with meal: {meal}")
    conn = sqlite3.connect('palate.db')
    cursor = conn.cursor()
    user_id = meal.get('userID')  # Assuming the key is 'userID'
    meal_id = meal.get('mealID')      # Assuming the key for meal ID is 'id'

    if user_id is not None and meal_id is not None:
        cursor.execute("""
            INSERT INTO food_journal_new (userID, mealID, liked)
            VALUES (?, ?, 1)
        """, (user_id, meal_id))
        conn.commit()
        print(f"Successfully added meal ID {meal_id} for user {user_id} to food_journal_new.")
    else:
        print("Error: Could not extract userID or id from the meal data.")
    conn.close()

if st.session_state.get('weekly_menu'):
    if st.session_state.get('current_meal_index', 0) < len(st.session_state['weekly_menu']):
        current_meal = st.session_state['weekly_menu'][st.session_state['current_meal_index']]
        st.markdown(
            f"<h3 style='font-family: Arial, sans-serif;'>{current_meal.get('name', 'Unnamed Meal')}</h3>",
            unsafe_allow_html=True,
        )
       
        if 'description' in current_meal:  # Adjust key if needed
            st.markdown(
                f"<p style='font-family: Arial, sans-serif;'>{current_meal['description']}</p>",
                unsafe_allow_html=True,
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            dislike_button = st.button("👎 Dislike", key="dislike_" + str(st.session_state.get('current_meal_index', 0)))
        with col2:
            no_preference_button = st.button("😐 No Preference", key="no_preference_" + str(st.session_state.get('current_meal_index', 0)))
        with col3:
            like_button = st.button("❤️ Like", key=f"like_{st.session_state.get('current_meal_index', 0)}")

        if dislike_button:
            print("Like button was clicked!")
            record_preference("Dislike")
            st.session_state['current_meal_index'] += 1
            st.rerun()
        elif no_preference_button:
            record_preference("No Preference")
            st.session_state['current_meal_index'] += 1
            st.rerun()
        elif like_button:
            record_preference("Like")
            add_liked_meal(current_meal)
            st.session_state['current_meal_index'] += 1
            st.rerun()
    else:
        st.write("--- Your Preferences ---")
        st.write(st.session_state['user_preferences'])
else:
    st.info("Fetching menu...")

