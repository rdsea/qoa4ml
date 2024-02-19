from tinydb import TinyDB, Query
import time

if __name__ == "__main__":
    db = TinyDB("db.json")
    db.truncate()
    while True:
        db.insert({"type": "apple", "count": 7})
        time.sleep(0.1)
