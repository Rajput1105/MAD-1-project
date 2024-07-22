import sqlite3

def create_tables():
    # Connect to the SQLite database. If the file does not exist, it will be created.
    conn = sqlite3.connect('mydatabase.db')
    
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Create the admin table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create the sponsor table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sponsor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        budget REAL NOT NULL,
        industry TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create the influencer table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS influencer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        influencer_name TEXT NOT NULL,
        target_audience INTEGER NOT NULL,
        youtube BOOLEAN,
        instagram BOOLEAN,
        twitter BOOLEAN,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Tables created successfully")

if __name__ == "__main__":
    create_tables()
