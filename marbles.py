#! /usr/bin/env python
import math
import matplotlib.pyplot as plt
import random
import sys
import operator as op
from functools import reduce

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    if numer <= denom:
        return 0
    else:
        return numer / denom

def iterGrab(marbles, original, toGrab, iterations=1000):
    noOverlap = 0
    for i in range(iterations):
        grab = random.sample(marbles, toGrab)
        intersection = list(set(grab) & set(original))

        if len(intersection) == 0:
            noOverlap += 1
    
    return noOverlap

def graph(data, comp, numMarbles):
    plt.plot(data, label="Experimental data")
    plt.plot(comp, label="Computation data")
    plt.title("Probability of not repeating marbles in grab (" + str(numMarbles) + " total marbles)")
    plt.xlabel("Number of marbles grabbed")
    plt.ylabel("Probability of no repeated marbles")
    plt.legend()
    plt.show()

def saveData(noOverlap, computation, numMarbles, its):
    f = open("marbles-" + str(numMarbles), "w")
    f.write("Experimental\t Computational\n")
    i = 1
    numDigits = int(math.log10(its))
    for a, b in zip(noOverlap, computation):
        f.write("{:02d}: {:s} ({:0.3f})\t {:f}\n".format(i, str(a).zfill(numDigits), a/float(its), b))
        i += 1
    f.close()

def experiment(marbles):
    iterations = 1000
    noOverlap = []
    computation = []
    for toGrab in range(1, len(marbles)):
        original = random.sample(marbles, toGrab)
        noOverlap.append(iterGrab(marbles, original, toGrab, iterations))
        computation.append(ncr(len(marbles)-toGrab, toGrab)/float(ncr(len(marbles),toGrab)))
        print("noOverlap, " + str(toGrab) + ": " + str(noOverlap[toGrab-1]))
        print("probability, " + str(toGrab) + ": " + str(computation[toGrab-1]))
    
    saveData(noOverlap, computation, len(marbles), iterations)

    noOverlap = [x/float(iterations) for x in noOverlap]
    graph(noOverlap, computation, len(marbles))


def main():
    if len(sys.argv) < 2:
        print("need 1 arguments, total number of marbles.")
        sys.exit(1)
    numMarbles = int(sys.argv[1])

    marbles = range(numMarbles)
    experiment(marbles)
    


if __name__ == "__main__":
    main()