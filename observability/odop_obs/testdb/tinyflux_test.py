from tinyflux import TinyFlux, Point
from tinyflux.storages import MemoryStorage
import time, datetime

db = TinyFlux(storage=MemoryStorage)

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
for i in range(0, 31536000):
    db.insert(p1)

while True:
    pass
