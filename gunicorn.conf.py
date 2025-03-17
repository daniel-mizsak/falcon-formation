"""
Configuration file for Gunicorn.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

# bind = "0.0.0.0:80"
bind = "0.0.0.0:5000"
workers = 2
timeout = 120
