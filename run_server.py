"""
Run the server on the host.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from falcon_formation.server import server

if __name__ == "__main__":
    server.run(host="0.0.0.0")
