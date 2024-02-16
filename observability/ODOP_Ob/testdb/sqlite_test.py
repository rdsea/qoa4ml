import sqlite3
import time

# 10MB
if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")

    c = conn.cursor()

    c.execute(
        """CREATE TEMPORARY TABLE IF NOT EXISTS temp_fruits (type TEXT, count INTEGER)"""
    )

    while True:
        c.execute("INSERT INTO temp_fruits VALUES ('apple', 7)")
        c.execute("INSERT INTO temp_fruits VALUES ('peach', 3)")

        conn.commit()

        c.execute("SELECT * FROM temp_fruits")
        for row in c.fetchall():
            print(row)

        time.sleep(10)
