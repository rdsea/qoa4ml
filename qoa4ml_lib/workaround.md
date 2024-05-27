# Ryu package:
Change 
```
from eventlet.wsgi import ALREADY_HANDLED 
```
to
```
import eventlet.wsgi
ALREADY_HANDLED = getattr(eventlet.wsgi, "ALREADY_HANDLED", None)
```

Or use two virtual env
