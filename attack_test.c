#include <igraph.h>

#include<string.h>

#include "attack.h"
#include "graph_gen.h"
#include "sms_gen.h"

int setup_run_attack(igraph_t g, int num_users, int num_epochs, int msgs_per_epoch, bool rr, int id, int sizes[20]) {
    Message mLog[id][msgs_per_epoch];
    Targets poi = create_log(num_epochs, msgs_per_epoch, g, rr, mLog);
    int possible_senders[num_users];
    possible_senders[0] = -1;
    sizes[0] = num_users;
    int needed_epochs = attack(id, msgs_per_epoch, mLog, poi, num_users, possible_senders, sizes);

    return needed_epochs;
}

void possible_senders_per_iteration_data(int num_users, int num_epochs, int msgs_per_epoch, bool rr, int id, int max_iterations, int msgs_per_epoch_mult) {
    char file_name1[50];
    // char file_name2[50];
    // char file_name3[50];
    // char file_name4[50];
    // char file_name5[50];
    // char file_name6[50];
    // char file_name7[50];
    sprintf(file_name1, "data/erdos_renyi_%d_%d.dat", num_users, msgs_per_epoch_mult);
    // sprintf(file_name2, "data/watts_strogatz_%d.dat", num_users);
    // sprintf(file_name3, "data/barabasi_%d.dat", num_users);
    // sprintf(file_name4, "data/full_%d.dat", num_users);
    // sprintf(file_name5, "data/star_%d.dat", num_users);
    // sprintf(file_name6, "data/star_off_center_%d.dat", num_users);
    // sprintf(file_name7, "data/ladder_%d.dat", num_users);

    FILE *data_file1 = fopen(file_name1, "w");
    // FILE *data_file2 = fopen(file_name2, "w");
    // FILE *data_file3 = fopen(file_name3, "w");
    // FILE *data_file4 = fopen(file_name4, "w");
    // FILE *data_file5 = fopen(file_name5, "w");
    // FILE *data_file6 = fopen(file_name6, "w");
    // FILE *data_file7 = fopen(file_name7, "w");
    for (int i = 0; i < max_iterations; i++ ) {
        printf("iteration %d, mult %d\n", i+1, msgs_per_epoch_mult);
        igraph_t g;
        igraph_erdos_renyi_game(&g, IGRAPH_ERDOS_RENYI_GNM, num_users, 90.0*num_users, IGRAPH_UNDIRECTED, IGRAPH_LOOPS);
        int sizes[20];
        int needed_epochs;
        needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        for(int i = 0; i < needed_epochs-1; i++) {
            fprintf(data_file1, "%d, ", sizes[i]);
        }
        fprintf(data_file1, "%d\n", sizes[needed_epochs-1]);
        fflush(data_file1);

        igraph_destroy(&g);
        // igraph_watts_strogatz_game(&g, 2, (igraph_integer_t) sqrt((double)num_users), (igraph_integer_t) log((double) num_users), 0.5, IGRAPH_LOOPS, IGRAPH_MULTIPLE);
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file2, "%d, ", sizes[i]);
        // }
        // fprintf(data_file2, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file2);

        // igraph_destroy(&g);
        // igraph_barabasi_game(&g, num_users, /*power*/ 1, /*outgoing edges*/ 90, NULL, true, /*A*/ 1, /*directed*/ false, IGRAPH_BARABASI_PSUMTREE_MULTIPLE, NULL);
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file3, "%d, ", sizes[i]);
        // }
        // fprintf(data_file3, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file3);
        // igraph_destroy(&g);

        // igraph_vector_t v;
        // igraph_vector_init(&v, 0);
        // igraph_create(&g, &v, num_users, 0);
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file4, "%d, ", sizes[i]);
        // }
        // fprintf(data_file4, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file4);
        // igraph_destroy(&g);
        // igraph_star(&g, num_users, IGRAPH_STAR_UNDIRECTED, 0); // person being attacked is connected to everyone.
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file5, "%d, ", sizes[i]);
        // }
        // fprintf(data_file5, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file5);
        // igraph_destroy(&g);
        // igraph_star(&g, num_users, IGRAPH_STAR_UNDIRECTED, 1); // person being attacked is connected only to the center.
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file6, "%d, ", sizes[i]);
        // }
        // fprintf(data_file6, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file6);
        // igraph_destroy(&g);

        // ladder_graph(&g, num_users);
        // memset(sizes, 0, 20*sizeof(int));
        // needed_epochs = setup_run_attack(g, num_users, num_epochs, msgs_per_epoch, rr, id, sizes);

        // for(int i = 0; i < needed_epochs-1; i++) {
        //     fprintf(data_file7, "%d, ", sizes[i]);
        // }
        // fprintf(data_file7, "%d\n", sizes[needed_epochs-1]);
        // fflush(data_file7);
        // igraph_destroy(&g);
    }
    fclose(data_file1);
    // fclose(data_file2);
    // fclose(data_file3);
    // fclose(data_file4);
    // fclose(data_file5);
    // fclose(data_file6);
    // fclose(data_file7);
}

void main() {
    int num_epochs = 30;
    int msgs_per_user_per_day = 50;
    int msgs_per_epoch_mult[9] = {1, 5, 10, 30, 60, 300, 600, 1800, 3600};
    for (int i = 0; i < 9; i++) {
        for(int num_users = 10000; num_users < 100000; num_users += 5000) {
            printf("num users: %d\n", num_users);
            int msgs_per_epoch = ((msgs_per_user_per_day * num_users)/(24*60*60))*msgs_per_epoch_mult[i];
            if (msgs_per_epoch <= 1) {
                printf("not enough users for assuming 50 messages per day per user\n");
                exit(1);
            }
            int id;
            bool rr = true; 
            if(rr){
                id = 2*num_epochs;
            }
            else {
                id = num_epochs;
            }
            int max_iterations = 100;

            possible_senders_per_iteration_data(num_users, num_epochs, msgs_per_epoch, rr, id, max_iterations, msgs_per_epoch_mult[i]);
        }
    }
}