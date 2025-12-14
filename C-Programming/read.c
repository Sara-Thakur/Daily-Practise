#include<stdio.h>
#include<string.h>
int main(){
    FILE *ptr;
    ptr = fopen("text.txt","r");
    int n; int i;

    fscanf(ptr,"%d",&n);
    for (int i=0;i<5;i++){ 
        printf("number=%d \n",n );
    fscanf(ptr,"%d",&n);
   }
   
    
return 0;
}