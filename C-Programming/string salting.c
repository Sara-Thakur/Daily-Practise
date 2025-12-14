#include<stdio.h>
#include<string.h>
void salting(char password[]);
int main(){
    char password[100];
    scanf("%s",password);
   void salting(char password[]){
        char salt[]="123";
        strcat(password,salt);
        puts(password);
    }
        salting(password);

}
 