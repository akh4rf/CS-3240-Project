
import socket
if socket.gethostbyname(socket.gethostname())[0:3]=="172":
    from .local_settings import *
else:
    from .production_settings import *