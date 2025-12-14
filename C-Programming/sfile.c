#include<stdio.h>
#include<string.h>
int main(){
    FILE *fptr;
    fptr=fopen("student.txt","w");
    char name[100];int age;float cgpa;
    printf("Enter name ");
    scanf("%s",name);
    printf("\nage ");
    scanf("%d",&age);
    printf("cgpa ");
    scanf("%f",&cgpa);
fprintf(fptr,"\n%s\t",name);
fprintf(fptr,"%d\t",age);
fprintf(fptr,"%f",cgpa);

}