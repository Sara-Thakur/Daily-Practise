#include <stdio.h>

int main()
{
    int var = 10;

    // declare pointer variable
    int *ptr=&var;

    // note that data type of ptr and var must be same
 int v=*ptr;

    // assign the address of a variable to a pointer

    printf("Value at var = %p \n", &var);
    printf("Value at ptr = %d \n", ptr);
     printf("Value at v = %d \n", &ptr);
}

