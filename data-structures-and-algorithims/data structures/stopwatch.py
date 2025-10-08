

#-----------------------------------------------------------------------
# stopwatch.py
#-----------------------------------------------------------------------


import time


#-----------------------------------------------------------------------

class Stopwatch:

    # Construct self and start it running.
    def __init__(self):
        self._creationTime = time.time()  # Creation time

    # Return the elapsed time since creation of self, in seconds.
    def elapsedTime(self):
        return time.time() - self._creationTime

#-----------------------------------------------------------------------

# For testing.
# Accept integer n as a command-line argument. Compare the performance
# of squaring integers using i**2 vs. i*i for the task of computing the
# sum of the squares of the integers from 1 to n.

