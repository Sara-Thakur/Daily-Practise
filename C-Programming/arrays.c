#include <stdio.h>
int main(){
    int adhar[5];
    int *pt =&adhar[0];
    for(int i=0;i<5;i++){
        printf("%d index:",i);
        scanf("%d",&adhar[i]);}
    for(int i=0;i<5;i++){
        printf("%d index:%d \n",i,adhar[i]);
    }
    }
