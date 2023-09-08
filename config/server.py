import random

RANDOM_PORT = True
if RANDOM_PORT:
    SERVER_PORT = random.randint(1024, 65535)
    DEBUG_PORT = random.randint(1024, 65535)
    if SERVER_PORT == DEBUG_PORT:
        DEBUG_PORT = random.randint(1024, 65535)
else:
    SERVER_PORT = 8080
    DEBUG_PORT = 5000

# The host on which the server will be running
SERVER_HOST = "localhost:" + str(SERVER_PORT)
# The URL on which the server will be running
"""
The protocol of the server should always be HTTP.
because the server is running on the localhost.
since the server is running on the localhost, we won't need HTTPS.
@resource: https://security.stackexchange.com/questions/246353/ssl-certificate-for-desktop-app
"""
SERVER_URL = "http://" + SERVER_HOST
