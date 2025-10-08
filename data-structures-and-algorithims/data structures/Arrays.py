from stopwatch  import Stopwatch
watch = Stopwatch()

import time




numbers=[8,
  30,
 -30,
 -20,
 -10,
  40,
   0,
  10,
  15]
def countTriples(a):
    n = len(a)
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n):
                if (a[i] + a[j] + a[k]) == 0:
                    count += 1
    print("Elapsed time:", watch.elapsedTime(), "seconds")
countTriples(numbers)



