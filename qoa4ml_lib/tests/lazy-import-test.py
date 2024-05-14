import time

start = time.time()
from typing import TYPE_CHECKING

import lazy_import

USE_TF = False

# import tensorflow as tf

if TYPE_CHECKING:
    import tensorflow as tf
else:
    tf = lazy_import.lazy_module("tensorflow")

print(f"Start up time: {time.time() - start}")
if USE_TF:
    test = tf.constant(4)
    print(test)
else:
    print("NOT use")
