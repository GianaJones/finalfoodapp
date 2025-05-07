import requests
import json
import time
from datetime import datetime
import pandas as pd
import csv
import streamlit as st
import numpy
import sqlite3
from  auth import google_login
from userProfile import render_user_profile
from pushDBtoPrivate import download_db_from_github
from auth import get_google_user_info
from UserSpecificDBs import init_user_db
from UserSpecificDBs import init_fj_db
import os

st.write("Pages found:", os.listdir("pages"))

#download_db_from_github()
#DEBUG=False
google_login()
first_name, last_name, email = get_google_user_info()
init_user_db()
init_fj_db()

conn = sqlite3.connect("users_new")
cursor = conn.cursor()

# Table for individual users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_new (
        userID PRIMARY KEY,
        firstName TEXT,
        lastName TEXT,
        diningHall TEXT,
        allergies TEXT,
        restrictions TEXT    
    )
''')
conn.commit()
conn.close()

#Storing user in users_new database
first_name, last_name, email = get_google_user_info()

conn = sqlite3.connect("users_new")
cursor = conn.cursor()

#Checking if user exists
cursor.execute('''
    SELECT firstName FROM users_new WHERE userID = ? AND lastName = ?
''', (email, last_name))
user = cursor.fetchone()

#Printing Welcome message if user in database adding user to database if not
if user:
    st.header(f"Welcome back, {first_name}!")

else:
    cursor.execute('''
        INSERT INTO users_new (userID, firstName, lastName)
        VALUES (?, ?, ?)
''', (email, first_name, last_name))
    
    conn.commit()
    st.header(f"Welcome to MyPalate, {first_name}!")


# Table for individual users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_new (
        userID PRIMARY KEY,
        firstName TEXT,
        lastName TEXT,
        diningHall TEXT,
        allergies TEXT,
        restrictions TEXT    
    )
''')
conn.commit()
conn.close()

#############################################################
#App Theme
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
body, h1, h2, h3, h4, h5, h6, p, label, button, div, input, select, option {
    font-family: 'Shadows Into Light', cursive !important;
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

#DEBUG = False #keep false when testing login
DEBUG = True # keep true when don't want to go throuhg testing


def get_week_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {"date": date, "locationID": locationID, "mealID": mealID}
    result = requests.get(base_url, params=params).text
    data = json.loads(result)
    return pd.DataFrame(data)

def get_day_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {"date": date, "locationID": locationID, "mealID": mealID}
    result = requests.get(base_url, params=params).text
    data = json.loads(result)
    df = pd.DataFrame(data)
    df = df[df["date"] == date]
    df = df.drop_duplicates(subset="id")
    if df.empty:
        st.info(f"No menu available for today {datetime.today}")
        return False
    return df

######################################################################################
#Rendering sidebar and pages (Tinder, Food Journal, Dashboard)


st.title("My Palate")
page_selected = st.sidebar.success("Menu")

#Manipulating date to match date in dataframe
date = str(st.date_input("Date: ")) + "T00:00:00"



#User selects dining hall and meal
dining_hall = st.selectbox("Dining Hall: ", ["Lulu", "Tower", "Stone D", "Bates"])
meal = st.selectbox("Meal: ", ["Breakfast", "Lunch", "Dinner"])



locationID = 0
mealID = 0
with open("wellesley-dining.csv", "r") as file:
    meals = pd.read_csv(file)

ids = pd.read_csv("wellesley-dining.csv")

def get_meal_and_location(df, loc, meal):
    """

    """
    if loc == "Lulu":
        loc = "Bao"
    matching_df = df[(df["location"] == loc) & (df["meal"] == meal)]
    locationID = matching_df["locationId"].iloc[0]
    mealID_avi = matching_df["mealID"].iloc[0]
    return locationID, mealID_avi


locationID, mealID_avi = get_meal_and_location(ids, dining_hall, meal)
def get_liked_meal_ids(userID):
    """Fetch mealIDs liked by the user."""
    conn = sqlite3.connect('food_journal_new')  # Replace with your database file path
    cursor = conn.cursor()
    cursor.execute("SELECT mealID FROM food_journal_new WHERE userID = ? AND liked = 1", (userID,))
    liked_meal_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return liked_meal_ids

if "show_menu" not in st.session_state:
    st.session_state["show_menu"] = False

show_menu = st.button("Show Menu")

if show_menu:
    st.session_state["show_menu"] = False
    menu_df = get_day_menu(date, locationID, mealID_avi)
    if isinstance(menu_df, pd.DataFrame) and not menu_df.empty:
        st.subheader(f"Menu for {dining_hall} on {date.split('T')[0]} - {meal}")
        liked_meal_ids = get_liked_meal_ids(email) # Use the user's email as userID
        for index, row in menu_df.iterrows():
            meal_name = row.get('name', 'No Name')
            meal_id = row.get('id') # Assuming 'id' in the menu_df corresponds to your mealID in food_journal_new
            description = row.get('description', 'No Description')
            heart_icon = "❤️" if meal_id in liked_meal_ids else ""
            st.markdown(f"<span style='font-family: Arial, sans-serif; font-size: 1.4em; font-weight: bold;'>{meal_name} {heart_icon}</span>", unsafe_allow_html=True)
            if description:
                st.markdown(f"<span style='font-family: Arial, sans-serif; font-size: 1.1em;'>{description}</span>", unsafe_allow_html=True)
                st.divider() # Add a visual separator between items
    elif menu_df is False:
        # The get_day_menu function already displays an info message
        pass
    else:
        st.info("No menu available for the selected date and meal.")



##########################################################################
#Set new preferences button

def update_meal_preferences(meal):
    cursor = sqlite3.connect("users")
    cursor.connect()

    cursor.execute('''
        INSERT INTO preferences[users], ?, meal
    ''')

preferences = st.button("Set new preferences")
if preferences and ('diet_rest' not in st.session_state):
    diet_rest = st.selectbox("Select dietary restrictions", ["Vegan", "Vegetarian", "Gluten Sensitive"]);
    allergies = st.selectbox("Select allergies", ["Eggs", "Fish", "Milk", "Peanuts", "Soy", "Sesame", "Shellfish", "Tree Nuts", "Wheat"])

    st.session_state['diet_rest'] = diet_rest
    st.session_state['allergies'] = allergies

#CLIENT_ID = st.secrets['google']['client_id']