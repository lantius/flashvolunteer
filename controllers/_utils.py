import os

def is_debugging():
    """Detects if app is running in production or not.

    Returns a boolean.
    """
    server_software = os.environ['SERVER_SOFTWARE']
    return server_software.startswith('Development')

