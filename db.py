import json
import logging
import psycopg2


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# Establish a database connection
def get_db_connection(dbname, user, password, host, port):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        logging.info("database connection successful")
        return conn
    except Exception as e:
        logging.error("database connection failed: %s", str(e))
        return None

# Function 1: Fetch email:password from emails
def fetch_emails(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT email, password FROM emails 
                WHERE 
                    (banned IS FALSE OR banned IS NULL) AND
                    (registered_in->>'render.com' IS NULL OR registered_in->>'render.com' = 'false')
                LIMIT 1000
            """)
            records = cur.fetchall()
            return records
    except Exception as e:
        logging.error(f"an error occurred: {e}")

# Function 2: Update row by email
def update_registration_status(conn, email):
    try:
        with conn.cursor() as cur:
            # Update the registered_in JSONB to include {"render.com": true}
            cur.execute("""
                UPDATE emails
                SET registered_in = jsonb_set(registered_in, '{render.com}', 'true')
                WHERE email = %s
            """, (email,))
            conn.commit()
            return 201
    except Exception as e:
        logging.error(f"an error occurred: {e}")
        return 500
