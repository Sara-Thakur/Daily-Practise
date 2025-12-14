#include <stdio.h>
#include<string.h>
#include<stdlib.h>
int main(){
    int *ptr;
    int n;
    printf("n:");
    scanf("%d",&n);
    ptr=malloc(5*sizeof(int));
    for(int i=0;i<5;i++){
        printf("%d\n",ptr[i]);}

ptr=realloc(ptr,8);
 for(int i=0;i<8;i++){
        printf("%d\n",ptr[i]);
    }
}
