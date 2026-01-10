import sqlite3

DB_NAME = "weather.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            area_code TEXT,
            date TEXT,
            weather TEXT,
            icon TEXT,
            min_temp TEXT,
            max_temp TEXT,
            PRIMARY KEY (area_code, date)
        )
    """)
    conn.commit()
    conn.close()

def save_forecasts(area_code, forecast_list):
    """
    Saves a list of forecast dictionaries to the DB.
    Uses 'INSERT OR REPLACE' to update existing data if fetched again.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for item in forecast_list:
        cursor.execute("""
            INSERT OR REPLACE INTO forecasts (area_code, date, weather, icon, min_temp, max_temp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            area_code,
            item["date"],
            item["weather"],
            item["icon"],
            item["min"],
            item["max"]
        ))
    
    conn.commit()
    conn.close()

def get_forecasts(area_code):
    """Retrieves weather data from the DB for a specific area."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, weather, icon, min_temp, max_temp 
        FROM forecasts 
        WHERE area_code = ? 
        ORDER BY date ASC
    """, (area_code,))
    
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "date": row[0],
            "weather": row[1],
            "icon": row[2],
            "min": row[3],
            "max": row[4]
        })
    return results