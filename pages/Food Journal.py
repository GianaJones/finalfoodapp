import streamlit as st
import sqlite3
from datetime import datetime
from myPalate import get_day_menu
from myPalate import get_meal_and_location
from myPalate import ids
from auth import get_google_user_info
from datetime import timedelta
from pages.Dashboard import get_macronutrients
from pages.Dashboard import get_entry


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
.stSelectbox > div > div > div {
background-color: #DAD7CD;    
}
.stMultiSelect > div > div > div {
        background-color: #DAD7CD !important; /* Replace with your color */
    }

    /* Target the dropdown options when the multiselect is open */
div[role="listbox"] ul {
    background-color: #DAD7CD !important; /* Replace with your color */
}
.st-an.st-ao.st-ap.st-aq.st-ak.st-ar.st-am.st-as.st-at.st-au.st-av.st-aw.st-ax.st-ay.st-az.st-b0.st-b1.st-b2.st-b3.st-b4.st-b5.st-b6.st-b7.st-b8.st-b9.st-ba.st-bb.st-cs  {
background-color: #DAD7CD;}
.st-emotion-cache-b0y9n5.e486ovb8  { 
  background-color: #DAD7CD !important;
}
</style>
""", unsafe_allow_html=True,
) 

conn = sqlite3.connect("palate.db")
cursor = conn.cursor()
# Table for food journal
cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_journal_new (
        entryID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER,
        mealID TEXT,
        dining_hall TEXT,
        date TEXT,
        liked BOOLEAN,
        FOREIGN KEY (userID) REFERENCES users(userID),
        FOREIGN KEY (mealID) REFERENCES meals(mealID)
    )
''')

conn.commit()
conn.close()


#Returns the meal name given the meal id
def get_meal_name(mealID):
    conn = sqlite3.connect("palate.db")
    cursor = conn.cursor()

    cursor.execute('''
    SELECT name, categoryName FROM meals WHERE mealID = ?
    ''', (mealID,))

    name = cursor.fetchone()
    
    if name is None:
        return "Item not in database"
    return name[0]

#Given user id, mealID, dining hall id, date, and liked status stores in food journal database
def store_entry(
        user_id: str,
        mealID: str,
        dining_hall: int,
        date: str,
        liked: bool):
    conn = sqlite3.connect("palate.db")
    cursor = conn.cursor()

    # Fetch user_id
    #first_name, last_name, user_id = get_google_user_info()

    # Insert entry record and get its ID
    cursor.execute('''
        INSERT INTO food_journal_new (userID, mealID, dining_hall, date, liked)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, mealID, dining_hall, date, liked))
    

    conn.commit()
    conn.close()

tab1, tab2 = st.tabs(["Add Entry", "View Entries"])

with tab1:
    st.title("Food Journal")
    st.header("Add Entry")

    with st.form("Journal Entry"):
        dining_hall = st.selectbox("Where?", ["Lulu", "Tower", "Stone D", "Bates"])
        meal = st.selectbox("When?", ["Breakfast", "Lunch", "Dinner"])
        locationID, mealID = get_meal_and_location(ids, dining_hall, meal )
        today = datetime.today()
        default_date = datetime.today().date()
        date = st.date_input("Date: ", value = default_date)
        date_formatted = str(date) + "T00:00:00"
        meals = get_day_menu(date_formatted, locationID, mealID)
        meals_for_day = []
        try:
            for i in range(len(meals)):
                meals_for_day.append(meals.iloc[i]['name'])
            selections = st.multiselect("What?", meals_for_day) 
        except TypeError:
                    st.write("No menu available.")

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if "selections_ids" not in st.session_state:
                st.session_state["selections_ids"] = []
            
            for idx, row in meals.iterrows():
                if row["name"] in selections:
                    st.session_state["selections_ids"].append(row["id"])

            dish_ids_selected = st.session_state["selections_ids"]
            first_name, last_name, user_id = get_google_user_info()
            locationID = str(locationID)
            if len(dish_ids_selected) != 0:
                for selection in dish_ids_selected:
                    store_entry(user_id, selection, locationID, date, False)
                st.success(f"Entry added for {meal} at {dining_hall} on {date}!")
            else:
                st.warning("No meals selected.")

    #Table header
    header_cols = st.columns([2, 1.5])
    header_cols[0].markdown("#### Dish")
    header_cols[1].markdown("#### Like")

    st.markdown("---")
        
    liked_ids = []

    first_name, last_name, user_id = get_google_user_info()

    # Loop through each row of the dataframe
    if "selections_ids" in st.session_state:
        for item in st.session_state["selections_ids"]:
            if item not in st.session_state:
                st.session_state[item] = False
            col1, col2= st.columns([2, 1])
            name = get_meal_name(str(item))
            col1.write(name)
            with col2:            
                #Getting the meals in selections that are already liked
                conn = sqlite3.connect("palate.db")
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT liked FROM food_journal_new
                    WHERE userID = ? AND mealID = ?
                """, (user_id, item))
                already_liked = cursor.fetchone()
                already_liked = already_liked[0] == 1 if already_liked else False
                st.session_state[item] = st.checkbox("Like?", key=f"check_{item}", value = already_liked)
                #if not already_liked and st.session_state[item]:
                if st.session_state[item] != already_liked:
                    cursor.execute("""
                        UPDATE food_journal_new
                        SET liked = ?
                        WHERE userID = ? and mealID = ?
                    """,(True if st.session_state[item] else False, user_id, item))
                    conn.commit()
            
            conn.close()

            if st.session_state[item]:
                for idx, row in meals.iterrows():
                    if item == row["name"]:
                        st.session_state["selections_ids"].append(row["id"])
                    else:
                        if item == row["name"] and row["id"] in st.session_state["selection_ids"]:
                            st.session_state["selection_ids"].remove(row["id"])
with tab2:
    st.title("Food Journal")
    st.header("View Entries")

#Modified calories getter defined in dashboard to take a date as a parameter
    def get_calories(date):
        first_name, last_name, user_id = get_google_user_info()
        calories = []
        meals = []
        meals = get_entry(user_id, date)
        st.write(meals)
        try:
            st.write(meals[0])
            calories_add = get_macronutrients(meals[0])['calories']
            meals.append(get_meal_name(meals[0]))
            calories.append(calories_add)
            data= {
                'Day': date,
                'Meal': meals,
                'Calories': calories
            }
            return data
        except:
            st.error("No data in Food Journal. Please make sure you are signed in!")

    date = st.date_input("Date: ")    
    col1, col2, col3 = st.columns(3)

    week_days = [date + timedelta(days=-i) for i in range(7)]
    week_days = [item.strftime("%Y-%m-%d") for item in week_days]
    #week_days = [item.strftime("%Y-%m-%d") + "T00:00:00" for item in week_days]

    data = []

    for day in week_days:
        #st.write(get_calories(day))
        data.append(get_calories(day))
    
    st.write(data)

    with col1:
        st.header("Date")
        try:
            for item in data:
                if item:
                    st.write(item["Day"])
                else:
                    st.write("No entry.")
        except:
            st.error("No data.")
    
    with col2:
        st.header("Meal")
        for i in range(len(data)):
            try:
                for item in data[i]["Meal"][0]:
                    if item:
                        st.write(item)
                    elif item is None:
                        st.write("No entry.")
            except:
                st.write("No entry.")

    with col3:
        st.header("Calories")
        for i in range(len(data)):
            try:
                for item in data[i]["Calories"]:
                    if item:
                        st.write(item)
                    elif item is None:
                        st.write("No entry.")
            except:
                st.write("No entry.")