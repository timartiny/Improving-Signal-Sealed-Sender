from igraph import *
import matplotlib.pyplot as plt

def ccdfsemilogx(g):
    degs = g.degree()
    counts = [degs.count(i) for i in range(max(degs)+1)]
    total = float(sum(counts))
    ccdf = [sum(counts[i:])/total for i in range(len(counts))]
    plt.semilogx(range(len(ccdf)), ccdf)
    plt.show()

def main():
    nodes = 1000000
    edges = 90*nodes
    g = Graph.Erdos_Renyi(n = nodes, m = edges)
    g.write_edgelist('graph.tmp')
    # ccdfsemilogx(g)

if __name__ == "__main__":
    main()
