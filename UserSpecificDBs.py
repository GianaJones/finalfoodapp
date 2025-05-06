import sqlite3
#from pushDBtoPrivate import get_db_path

DB_NAME = "users_new"
DB_NAME2 = "food_journal_new"
def init_user_db():
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
    conn.commit()
    conn.close()
    
    
def init_fj_db():   
    conn = sqlite3.connect(DB_NAME2)
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
