import sys

from server import server


# Running server
serv = server(port=int(sys.argv[1]))
serv.run()