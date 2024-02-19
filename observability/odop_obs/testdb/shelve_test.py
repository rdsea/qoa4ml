import shelve, time

d = shelve.open("./shevel_test.db")  # open -- file may get suffix added by low-level
i = 0  # library
while True:
    start = time.time()
    d[str(i)] = {"type": "apple", "count": 7}
    print(f"latency {(time.time() - start)*1000}ms")
    i += 1
    time.sleep(1)
