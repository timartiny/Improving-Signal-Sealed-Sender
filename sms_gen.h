#ifndef SMS_GEN_H
#define SMS_GEN_H
#include <stdbool.h>
typedef struct Messages {
    double time;
    int type;
    int from;
    int to;
} Message;

typedef struct Target {
    int sender;
    int receiver;
} Targets;

int get_adjacent(igraph_t, igraph_integer_t);
void generate_senders(size_t, igraph_t, int[][2]);
Targets create_log(int, int msgs_per_epoch, igraph_t, bool, Message[][msgs_per_epoch]);
void generate_repeats(size_t, size_t od, Message[][od], int[][2], bool, double);
void generate_responses(size_t, size_t od, Message[][od], int[][2], bool, double);
void print_log(size_t, size_t od, Message[][od]);
void print_senders(size_t, size_t od, int[][od]);
void new_senders(size_t, size_t od, Message[][od], int[od][2], bool, double, double, igraph_t, int);
#endif