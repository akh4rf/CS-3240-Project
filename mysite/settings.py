
import socket
host = socket.gethostbyname(socket.gethostname())
if (host[0:3]=="172" or host[0:3]=="192" or host[0:3]=="127"):
    from .local_settings import *
else:
    from .production_settings import *
