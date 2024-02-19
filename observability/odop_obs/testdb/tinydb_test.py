from tinydb import TinyDB, Query
import time

if __name__ == "__main__":
    db = TinyDB("db.json")
    db.truncate()
    while True:
        start = time.time()
        db.insert({"type": "apple", "count": 7})
        print(f"latency {(time.time() - start)*1000}ms")
        time.sleep(1)
