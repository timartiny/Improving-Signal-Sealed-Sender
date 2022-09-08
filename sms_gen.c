#include <igraph.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "graph_gen.h"
#include "sms_gen.h"

int get_adjacent(igraph_t g, igraph_integer_t v) {
    igraph_vs_t vs;
    igraph_vit_t vit;
    igraph_es_t es;
    igraph_eit_t eit;
    int size;
    int count;

    igraph_es_all(&es, IGRAPH_EDGEORDER_ID);
    igraph_es_size(&g, &es, &size);
    if(size == 0) {
        // this corresponds to a full graph, cheaper way to store it.
        igraph_vs_all(&vs);
        igraph_vs_size(&g, &vs, &size);
        int r = rand() % size;
        return r;
    }

    igraph_vs_adj(&vs, v, IGRAPH_ALL);
    igraph_vs_size(&g, &vs, &size);
    igraph_vit_create(&g, vs, &vit);
    int r = rand() % size;
    // printf("r: %lu\n", r);
    // printf("nodes: ");
    count = 0;
    while((!IGRAPH_VIT_END(vit)) && (count < r)) {
        // printf("%li ", (long int) IGRAPH_VIT_GET(vit));
        IGRAPH_VIT_NEXT(vit);
        count++;
    }
    // printf("\n");

    int m = (int) IGRAPH_VIT_GET(vit);
    igraph_vs_destroy(&vs);
    igraph_vit_destroy(&vit);
    return m;
}

void generate_senders(size_t len, igraph_t g, int arr[][2]){
    igraph_vs_t vs;
    int graph_size;
    igraph_vs_all(&vs);
    igraph_vs_size(&g, &vs, &graph_size);
    for(int i = 0; i < len; i++){
        // choose sender, set receiver to -1
        int r = rand() % graph_size;

        arr[i][0] = r;
        arr[i][1] = -1;
    }
}

void print_log(size_t id, size_t od, Message log[][od]){
    for(int i = 0; i < id; i++){
        for(int j = 0; j < od; j++){
            Message m = log[i][j];
            printf("log[%d][%d]\n\t.time = %f\n\t.type = %d\n\t.from = %d\n\t.to = %d\n", i, j, m.time, m.type, m.from, m.to);
        }
    }
}

void print_senders(size_t id, size_t od, int arr[][od]){
    for(int i = 0; i < id; i++){
        for(int j = 0; j < od; j++){
            printf("arr[%d][%d] = %d\n", i, j, arr[i][j]);
        }
    }
}

/**
 * This function will fill arr array with max entries from log. id/od are inner/outer dimension of log
 * rr keeps track of whether we need to skip over some read receipts of log or not
 **/ 
void generate_repeats(size_t id, size_t od, Message log[][od], int arr[][2], bool rr, double max) {
    for(int i = 0; i < max; i++){
        int rid;
        // printf("id = %lu\n", id);
        if (id == 0){
            rid = 0;
        } else {
            rid = rand() % id;
        }

        if (rr && rid % 2 == 1 ) { // we've choosen a read receipt
            rid--;
        }
        int rod = rand() % od;
        arr[i][0] = log[rid][rod].from;
        arr[i][1] = log[rid][rod].to;
    }
}

/**
 * This function will fill arr with max entries as responses from entries in log. id/od are inner/outer
 * dimensions of log rr keeps track of whether we need to skip over some read receipts of log or not
 * 
 * arr is already scaled so that arr[0][0] is zero though previous entries should be filled out.
 * 
 * Next step is to figure out how to bias this to favor newer messages
 */ 
void generate_responses(size_t id, size_t od, Message log[][od], int arr[][2], bool rr, double max) {
    for(int i = 0; i < max; i++){
        int rid;
        if (id == 0){
            rid = 0;
        } else {
            rid = rand() % id;
        }

        if (rr && rid % 2 == 1 ) { // we've choosen a read receipt
            rid--;
        }
        int rod = rand() % od;
        arr[i][0] = log[rid][rod].to;
        arr[i][1] = log[rid][rod].from;
    }
}

void new_senders(size_t id, size_t od, Message log[][od], int senders[od][2], bool rr, double repeat_count, double response_count, igraph_t g, int marked_sender) {
    // now create new senders list, choose half to be new messages (as above) and half to be responses (or repeated messages)
    memset(senders, 0, 2*od*sizeof(int));
    generate_repeats(id, od, log, senders, rr, repeat_count);

    // printf("\nafter generate repeats\n");
    // print_log(id, od, log);
    // print_senders(od, 2, senders);

    generate_responses(id, od, log, senders+(unsigned long) ceil(repeat_count), rr, response_count);

    // printf("\nafter generate responses\n");
    // print_log(id, od, log);
    // print_senders(od, 2, senders);

    generate_senders(od-1-(unsigned long) ceil(repeat_count) - (unsigned long) ceil(response_count), g, senders+(unsigned long) ceil(repeat_count) + (unsigned long) ceil(response_count));
    senders[od-1][0] = marked_sender;
    senders[od-1][1] = 0;

    // printf("\nafter new messages\n");
    // print_senders(od, 2, senders);
}

Targets create_log(int num_epochs, int msgs_per_epoch, igraph_t g, bool rr, Message log[][msgs_per_epoch]){
    double const REPEAT_PERCENTAGE = 0.25;
    double const RESPONSE_PERCENTAGE = 0.25;
    srand(time(NULL));
    int marked_sender = get_adjacent(g, 0);
    // printf("chosen adjacent: %li\n", (long int) marked_sender);

    int id, loop_jump;
    if(rr){
        id = 2*num_epochs;
        loop_jump = 2;
    }
    else {
        id = num_epochs;
        loop_jump = 1;
    }
    
    // log of messages, each message has 4 parts (time, type, from, to)
    // there are msgs_per_epoch every epoch, and num_epochs number of epochs
    // the inner dimension (id) is twice as big if we have read recipts
    // generate senders for first loop
    int senders[msgs_per_epoch][2];

    generate_senders(msgs_per_epoch-1, g, senders);
    // last sender will be selected sent
    senders[msgs_per_epoch-1][0] = marked_sender;
    senders[msgs_per_epoch-1][1] = 0;
    double time = 0;
    for (int i = 0; i < id; i+=loop_jump){
        // now create messages 
        for(int j = 0; j < msgs_per_epoch; j++){
            // message will contain time sent, the type (0 for message 1 for read receipt), from person and to person
            log[i][j].time = time; 
            log[i][j].type = 0; 
            log[i][j].from = senders[j][0];
            if (senders[j][1] != -1) {
                log[i][j].to = senders[j][1];
            } else {
                log[i][j].to = get_adjacent(g, senders[j][0]);
            }

            if (rr) {
                log[i+1][j].time = time+0.5;
                log[i+1][j].type = 1;
                log[i+1][j].from = log[i][j].to;
                log[i+1][j].to = log[i][j].from;
            }
        } // end j loop (looping over each message in epoch)

        time++;
        new_senders(i, msgs_per_epoch, log, senders, rr, REPEAT_PERCENTAGE*msgs_per_epoch, RESPONSE_PERCENTAGE*msgs_per_epoch, g, marked_sender);
    }

    // printf("num_epochs = %d\n", num_epochs);
    // print_log(id, msgs_per_epoch, log);
    Targets ts;
    ts.sender = marked_sender;
    ts.receiver = 0;
    return ts;
}


// int main(){
//     igraph_t g;
//     genGraph(&g, 100000, "Erdos_Renyi");
//     int num_epochs = 10;
//     int msgs_per_epoch = 10;
//     int id;
//     bool rr = true; 
//     if(rr){
//         id = 2*num_epochs;
//     }
//     else {
//         id = num_epochs;
//     }
//     Message log[id][msgs_per_epoch];
//     create_log(num_epochs, msgs_per_epoch, g, true, log);
// }