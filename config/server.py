import random

RANDOM_PORT = True
if RANDOM_PORT:
    SERVER_PORT = random.randint(1024, 65535)
else:
    SERVER_PORT = 8080

# The host on which the server will be running
SERVER_HOST = "localhost:" + str(SERVER_PORT)
# The URL on which the server will be running
SERVER_URL = "http://" + SERVER_HOST
