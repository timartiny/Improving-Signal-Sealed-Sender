#! /usr/bin/env python3
import numpy as np
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

def processLines(lines):
    preSend = 0
    startTime = 0
    endTime = 0
    totalTime = 0
    its = 0
    data = []
    sending = []
    for line in lines:
        split = line.split(": ")
        if split[0] == "SignalServiceMessageSender":
            if split[2] == "pre-send":
                preSend = int(split[3])
            else:
                startTime = int(split[2])
        elif split[0] == "IncomingMessageProcesso":
            endTime =  int(line.split("DRCDF: ")[1])
        elif split[0] == "PushDecryptJob":
            l = line.split("DRCDF: ")[1].split(" -> ")
            if startTime == 0:
                startTime = int(l[0])
            if endTime == 0:
                endTime = int(l[1])

            data.append(endTime - startTime)
            if preSend:
                sending.append(startTime - preSend)
            totalTime += data[-1]
            its += 1

            preSend = 0
            startTime = 0
            endTime = 0
        # print("startTime: {}, endTime: {}, time per text: {}ms".format(startTime, endTime, totalTime/float(its)))
    
    sending=False
    print("Time per text: {:.02f}ms, averaged over {:d} messages".format(totalTime/float(its), its))
    num_bins = 20
    print('\n'.join([str(x) for x in data]))
    counts, bin_edges = np.histogram(data, bins=num_bins, normed=True)
    cdf = np.cumsum(counts)
    plt.plot(bin_edges[1:], cdf/cdf[-1], color='b')

    index_gt_50 = next(x[0] for x in enumerate(cdf/cdf[-1]) if x[1] > 0.50)
    print("index_gt_50: {}".format(bin_edges[index_gt_50+1]))
    index_gt_90 = next(x[0] for x in enumerate(cdf/cdf[-1]) if x[1] > 0.90)
    print("index_gt_90: {}".format(bin_edges[index_gt_90+1]))
    #plt.plot([bin_edges[index_gt_50+1]]*2, [0, 0.5], color='k', label="50% of Delivery Receipts")
    #plt.plot([bin_edges[index_gt_90+1]]*2, [0, 0.9], color='k', label="90% of Delivery Receipts")
    #plt.grid()
    plt.ylim(ymin=0, ymax=1)
    plt.xlim(xmin=0)
    plt.xlabel("Time (ms)")
    plt.ylabel("CDF")
    plt.legend(loc='center right')
    plt.savefig("DRCDF.pdf", format="pdf")
    plt.show()
    



def main():
    # with open("DRCDF-filtered.dat", 'r') as f:
    with open(sys.argv[1], 'r') as f:
    # with open("tmp.dat", 'r') as f:
        lines = f.readlines()
    
    # print(lines)
    lines = [line.split(" I ")[1] for line in lines]
    # print(lines)
    processLines(lines)
    
if __name__ == "__main__":
    main()
