#ifndef ATTACK_H
#define ATTACK_H
#include "sms_gen.h"
int cmpfunc (const void *, const void *);
int findIntersection(int arr1[], int arr2[], int max1, int max2, int retArr[max2]);
double findTimeOfMessageAfterTime(int, int od, Message log[][od], int, double); 
int readReceiptsAtTime(int, int od, Message[][od], double, int[od]);
int attack(int, int od, Message[][od], Targets, int sd, int[sd], int[20]);
#endif