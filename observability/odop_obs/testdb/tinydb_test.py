from tinydb import TinyDB, Query
import time

if __name__ == "__main__":
    db = TinyDB("db.json")
    db.truncate()
    while True:
        db.insert({"type": "apple", "count": 7})
        db.insert({"type": "peach", "count": 3})
        for item in db:
            print(item)
        time.sleep(10)
