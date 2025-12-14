#include<stdio.h>

 struct st{
        int roll;
        float cgpa;
        char name [100];
    };
    
int main() {
    struct st s1={1771,8.2,"shrad"};
    printf("roll =%d\n",s1.roll);
    struct st *ptr=&s1;
    printf("roll = %d \n",(*ptr).roll);
    printf("roll = %s \n",ptr->name);
    printf("roll = %d \n cgpa =%f \n",(*ptr).roll),ptr->cgpa);

    return 0;
}
  
  
            