#ifndef GRAPH_GEN_H
#define GRAPH_GEN_H
void genGraph(igraph_t*, int, char*);
double transitivity(const igraph_t *g);
void degree_stats(const igraph_t *);
void print_vector(const igraph_vector_t *);
void print_array(const long int[], int); 
long int minimum_degree(const igraph_vector_t *);
void ladder_graph(igraph_t*, int);
#endif