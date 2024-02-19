import sqlite3
import time

# 10MB
if __name__ == "__main__":
    conn = sqlite3.connect(":memory")

    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS temp_fruits (type TEXT, count INTEGER)""")

    for i in range(0, 2592000):
        c.execute("INSERT INTO temp_fruits VALUES ('apple', 7)")

        conn.commit()

    time.sleep(1000)
