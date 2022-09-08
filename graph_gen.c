#include <igraph.h>
#include <math.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "graph_gen.h"

// void genGraph(igraph_t* g, int nodes, char* method) {
//     if (strncmp(method, "Erdos_Renyi", 11) == 0){
//         igraph_erdos_renyi_game(g, IGRAPH_ERDOS_RENYI_GNM, nodes, 90.0*nodes,
//             IGRAPH_UNDIRECTED, IGRAPH_NO_LOOPS);
//     }
//     else if (strncmp(method, "Watts_Strogatz", 14) == 0){
//         igraph_watts_strogatz_game(g, 2, sqrt(double()), 5, 0.5, false, false);
//     }
//     // else if (strncmp(method, "Barabasi", 8) == 0){
//     //     igraph_barabasi_game(g, 
//     // }
// }

void ladder_graph(igraph_t* g, int nodes) {
    igraph_vector_t v;
    igraph_vector_init(&v, nodes);
    for(int i = 0; i < nodes; i+=2) {
        VECTOR(v)[i] = i;
        VECTOR(v)[i+1] = i+1;
    }

    igraph_create(g, &v, nodes, IGRAPH_UNDIRECTED);
}

double transitivity(const igraph_t *g) {
    igraph_real_t res;
    igraph_transitivity_undirected(g, &res, IGRAPH_TRANSITIVITY_NAN);
    return (double) res;
}

void print_vector(const igraph_vector_t *v) {
    for(long int i = 0; i < igraph_vector_size(v); i++) {
        printf("%li ", (long int) VECTOR(*v)[i]);
    }
    printf("\n");
}

void print_array(const long int arr[], int size) {
    for(int i = 0; i < size; i++ ){
        printf("%li ", arr[i]);
    }
    printf("\n");
}

long int minimum_degree(const igraph_vector_t *v) {
    long int min = (long int) VECTOR(*v)[0];
    for (int i = 0; i < igraph_vector_size(v); i++){
        if((long int) VECTOR(*v)[i] < min) {
            min = (long int) VECTOR(*v)[i];
        }
    }

    return min;
}

long int sumGreaterThan(long int arr[], const int size, int startInd) {
    long int res = 0;
    for(int i = startInd; i < size; i++){
        res += arr[i];
    }

    return res;
}

void degree_stats(const igraph_t *g) {
    // first find degree of every node
    igraph_vector_t degs;
    igraph_vector_init(&degs, 8);
    igraph_degree(g, &degs, igraph_vss_all(), IGRAPH_ALL, IGRAPH_NO_LOOPS);
    // now degs is a list of every node's degree
    // create an array of the number of nodes with each degree

    // printf("degrees: ");
    // print_vector(&degs);

    igraph_vs_t vs;
    igraph_integer_t size;

    igraph_integer_t max_degree;
    long int min_degree;
    igraph_vs_all(&vs);
    igraph_vs_size(g, &vs, &size);
    min_degree = minimum_degree(&degs);
    igraph_maxdegree(g, &max_degree, igraph_vss_all(), IGRAPH_ALL, IGRAPH_NO_LOOPS);
    long int degs_count[max_degree-min_degree]; // the degree of any edge is capped at the number of nodes
    memset(degs_count, 0, (max_degree-min_degree)*sizeof(long int));

    for(int i = 0; i < size; i++) {
        degs_count[((long int) VECTOR(degs)[i]) - min_degree]++;
    }
    // print_array(degs_count, size);

    // now degs_count is an array of how many nodes have each degree
    FILE *gnuplot = popen("gnuplot -persistent", "w");
    fprintf(gnuplot, "plot '-'\n");

    for(int i = 0; i < max_degree-min_degree; i++) {
        fprintf(gnuplot, "%li %f\n", i+min_degree,((double) degs_count[i])/size);
    }
    fprintf(gnuplot, "e\n");
    fflush(gnuplot);
    pclose(gnuplot);

    // now compute ccdf of degs.
    long int ccdf[max_degree-min_degree];
    for(int i = 0; i < max_degree-min_degree; i++) {
        ccdf[i] = sumGreaterThan(degs_count, max_degree-min_degree, i);
    }

    gnuplot = popen("gnuplot -persistent", "w");
    fprintf(gnuplot, "plot '-'\n");

    for(int i = 0; i < max_degree-min_degree; i++) {
        fprintf(gnuplot, "%li %f\n", i+min_degree,((double) ccdf[i])/size);
    }
    fprintf(gnuplot, "e\n");
    fflush(gnuplot);
    pclose(gnuplot);
}
