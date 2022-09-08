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
#include "attack.h"

int cmpfunc (const void * a, const void * b) {
   return ( *(int*)a - *(int*)b );
}

int findIntersection(int arr1[], int arr2[], int max1, int max2, int retArr[max2]) { 
    int i = 0, j = 0, rid = 0; 
    while (i < max1 && j < max2 && rid < max2) { 
        if (arr1[i] < arr2[j]) 
            i++; 
        else if (arr2[j] < arr1[i]) 
            j++; 
        else { /* if arr1[i] == arr2[j] */ 
            retArr[rid++] = arr2[j++];
            i++; 
        } 
    } 

    return rid;
} 

double findTimeOfMessageAfterTime(int id, int od, Message log[][od], int person_of_interest, double t) {
    for(int i = 0; i < id; i++){
        if(log[i][0].time <= t)
            continue;

        if(ceilf(log[i][0].time) == log[i][0].time){
            // further work needs to ensure there is a message to the person of interest
            return log[i][0].time;
        }
    }
    return -1;
}

int readReceiptsAtTime(int id, int od, Message log[][od], double t, int rrs[od]) {
    int count = 0;
    for(int i = 0; i < id; i++) {
        if(log[i][0].time < t) // will eventually need to be a check for time in a range
            continue;
        if(log[i][0].time > t)
            break;
        
        if(log[i][0].type != 1) // right now all read receipts are in the same row, will change
            continue;
        
        // now in the correct id, loop through all messages to collect them
        for(int j = 0; j < od; j++) {
            rrs[count] = log[i][j].to;
            count++;
        }
    }

    return count;
}

int attack(int id, int od, Message log[][od], Targets poi, int sd, int possible_senders[sd], int sizes[20]) {
    // look at messages (ignoring "from") and determine which user was messaging person of interest (poi.receiver)
    // current assumptions: the rr is sent 0.5 seconds after messages always
    //                      messages always have a read receipt (rr)
    //                      user receives a message every second (no required replies)

    int real_sender = poi.sender;
    // printf("real sender: %d\n", real_sender);
    double prb = 0, time = -1;
    int necessary_epochs = 1;

    // continue looking at messages until we're more than 80% sure who the sender is
    // need more complex probability computation, right now it runs until we get exactly 1 user
    while(prb < 0.8) {
        time = findTimeOfMessageAfterTime(id, od, log, poi.receiver, time);
        if(time == -1) // reached end of log
            break;

        int rrs[od]; // list of read receipts from this time
        int rrlen = readReceiptsAtTime(id, od, log, time+0.5, rrs);
        // for(int i = 0; i < rrlen; i++){
        //     printf("rrs[%d]: %d\n", i, rrs[i]);
        // }

        if(possible_senders[0] != -1) { // not the first time through this loop
            int min = (rrlen < sd) ? rrlen : sd;
            int tmp_senders[min];
            qsort(rrs, rrlen, sizeof(int), cmpfunc);
            int intersection_size = findIntersection(possible_senders, rrs, sd, min, tmp_senders);
            bzero(possible_senders, sizeof(int)*sd);
            memcpy(possible_senders, tmp_senders, intersection_size*sizeof(int));
            // for(int i = 0; i < intersection_size; i++){
            //     printf("possible_senders[%d] = %d\n", i, possible_senders[i]);
            // }
            // printf("intersection_size: %d\n", intersection_size);
            sizes[necessary_epochs] = intersection_size;
            prb = 1.0/intersection_size;
        } else {
            if(rrlen >= sd) {
                printf("too many possible senders\n");
                return necessary_epochs;
            }
            memcpy(possible_senders, rrs, rrlen*sizeof(int));
            // for(int i = 0; i < rrlen; i++){
            //     printf("possible_senders[%d] = %d\n", i, possible_senders[i]);
            // }
            qsort(possible_senders, rrlen, sizeof(int), cmpfunc);
            sizes[necessary_epochs] = rrlen;
        }

        // printf("\n");
        necessary_epochs++;

    }
    // printf("took %d epochs\n", necessary_epochs);
    return necessary_epochs;
}