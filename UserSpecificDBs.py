import sqlite3
import pandas as pd
#from pushDBtoPrivate import get_db_path

DB_NAME = "palate.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
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

    #Table for all Wellesley Fresh meals
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals(
               mealID PRIMARY KEY,
               name text,
               description text
               categoryName text,
               allergens text, 
               preferences text,
               nutritionals text)
               """)
    
    #Populating meals table
    with open("wellesley-meals.csv", "r") as file:
        all_meals = pd.read_csv(file)

    all_meals.drop(columns = ["servingSize","servingSizeUOM","calories",
                                  "fat","caloriesFromFat","saturatedFat",
                                  "transFat","cholesterol","sodium","carbohydrates",
                                  "dietaryFiber","sugars","addedSugar","protein"], inplace = True)


    all_meals.columns = ["mealID", "name", "description", "categoryName", "allergens", "preferences", "nutritionals"]
    all_meals.to_sql("meals", conn, if_exists = "replace", index=False)


    conn.commit()
    conn.close()
