#include<stdio.h>
#include<stdlib.h>
#include<string.h>
int main(){
    int *ptr;
    ptr=(int*)calloc(5,sizeof(int));
    printf("enter 5 odd:");
    for(int i=0;i<5;i++){
        scanf("%d",&ptr[i]);}
    ptr=realloc(ptr,6);
    printf("real 6:");

    for(int i=0;i<6;i++){
        scanf("%d",&ptr[i]);}
    for(int i=0;i<6;i++){
            printf("number %d\n",ptr[i]);
    }
    free(ptr);
return 0;
}