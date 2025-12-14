#include<stdio.h>
#include<string.h>
int main(){
    FILE *fptr;
    fptr=fopen("area.c","r");
    if (fptr==NULL){
        printf("file not exist\n");

    }else {
            char ch;
    fscanf(fptr,"%c",&ch);
    printf("char = %c\n",ch);
    fscanf(fptr,"%c",&ch);
    printf("char = %c\n",ch);
    fscanf(fptr,"%c",&ch);
    printf("char = %c\n",ch);
    printf("%c",fgetc(fptr));
            fclose(fptr);
    } 
    return 0;
}