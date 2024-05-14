# import time
# import math
# from threading import Event, Thread
#
#
# def do_smt():
#     print(f"Start at {time.time()}")
#     time.sleep(0.1)
#     print("Done")
#
#
# class RepeatedTimer:
#
#     """Repeat `function` every `interval` seconds."""
#
#     def __init__(self, interval, function, *args, **kwargs):
#         self.interval = interval
#         self.function = function
#         self.args = args
#         self.kwargs = kwargs
#         self.start = time.time()
#         self.event = Event()
#         self.thread = Thread(target=self._target)
#         self.thread.start()
#
#     def _target(self):
#         if not hasattr(self, "test"):
#             print("waerasr")
#         self.function(*self.args, **self.kwargs)
#         while not self.event.wait(self._time):
#             self.function(*self.args, **self.kwargs)
#
#     @property
#     def _time(self):
#         return self.interval - ((time.time() - self.start) % self.interval)
#
#     def stop(self):
#         self.event.set()
#         self.thread.join()
#
#
# # start timer
# current_time = time.time()
# time.sleep(math.ceil(current_time) - current_time)
# print(time.time())
# timer = RepeatedTimer(1, do_smt)
# time.sleep(4.4)
# # stop timer
# timer.stop()
#

arr = []
append = arr.append
for i in range(1, 2**20):
    append(i)
