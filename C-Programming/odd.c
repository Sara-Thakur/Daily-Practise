#include<stdio.h>
#include<string.h>
int main() {
    FILE *fptr;
    fptr=fopen("student.txt","a");
    int n;int m;
    fscanf(fptr,"%d",&n);
    printf("first number")
    for(int  i=0;i<=n;i++){
        if (i %2 !=0){
            fprintf(fptr,"%d\n",i);
        }
    }
 
}