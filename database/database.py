import mysql.connector
import bcrypt
from mysql.connector import Error
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

# User Management
def add_user(username, password):
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to get DB connection")
        return False
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed.decode())
        )
        conn.commit()
        return True
    except Error as e:
        logging.error(f"Error inserting user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT password_hash FROM users WHERE username=%s",
            (username,)
        )
        row = cursor.fetchone()
    except Error as e:
        logging.error(f"Error querying user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return False

# Stock Data Management
def insert_stock(stock_record):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO stocks (symbol, date, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                stock_record['symbol'],
                stock_record['date'],
                stock_record['open'],
                stock_record['close'],
                stock_record['high'],
                stock_record['low'],
                stock_record['volume']
            )
        )
        conn.commit()
        return True
    except Error as e:
        logging.error(f"Error inserting stock data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_stock_data(symbol):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM stocks WHERE symbol=%s ORDER BY date DESC LIMIT 90",
            (symbol,)
        )
        results = cursor.fetchall()
        return results
    except Error as e:
        logging.error(f"Error fetching stock data: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# News Management
def insert_news(news_record):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO news (symbol, headline, summary, published_at) VALUES (%s, %s, %s, %s)",
            (
                news_record['symbol'],
                news_record['headline'],
                news_record['summary'],
                news_record['published_at']
            )
        )
        conn.commit()
        return True
    except Error as e:
        logging.error(f"Error inserting news: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_news(symbol):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM news WHERE symbol=%s ORDER BY published_at DESC",
            (symbol,)
        )
        results = cursor.fetchall()
        return results
    except Error as e:
        logging.error(f"Error fetching news: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
