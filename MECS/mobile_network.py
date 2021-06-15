import logging

log = logging.getLogger(__name__)

class connection:
    def __init__(self, *args, **kwds):
        self.connected = False

    def __enter__(self):
        # Make sure we connect
        self.connected = True
        # Demonstrate this is being called
        log.debug(self)
        # return the object for use as necessary
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Make sure we disconnect
        self.connected = False
        # demonstrate this is being called
        log.debug(self)
        # do not suppress exceptions
        return False


    def __repr__(self):
        return f"connection(connected={self.connected})"
