import sqlite3

try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute('PRAGMA table_info(posts)')
    columns = [info[1] for info in cursor.fetchall()]
    print(f'Current columns: {columns}')
    
    if 'upvotes' not in columns:
        print("Adding 'upvotes' column...")
        cursor.execute('ALTER TABLE posts ADD COLUMN upvotes INTEGER DEFAULT 0')
        conn.commit()
        print("Migration successful!")
    else:
        print("'upvotes' column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
