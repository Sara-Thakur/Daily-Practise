#include <stdio.h>
#include <string.h>

typedef struct bank_account_info{
    char name[100];
    int accno;
    }acc;
int main(){
    acc acc1={"heriye",123};
    acc acc2={"heryu",432};
     acc *ptr=&acc1;
    printf("acc no =%d", ptr->accno);
    return 0;
}