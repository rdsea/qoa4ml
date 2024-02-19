from tinyflux import TinyFlux, Point
import time, datetime

db = TinyFlux("./db.csv")
p1 = Point(
    time=datetime.datetime.now(),
    tags={"city": "LA"},
    fields={"aqi": 112},
)

p2 = Point(
    time=datetime.datetime.now(),
    tags={"city": "SF"},
    fields={"aqi": 128},
)
while True:
    start = time.time()
    db.insert(p1)
    print(f"latency {(time.time() - start)*1000}ms")
    time.sleep(1)
