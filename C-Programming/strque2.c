#include<stdio.h>
#include<string.h>
struct complex{
    int real;
    int img;
};
int main(){
    struct complex c1={3,4};
    struct complex c2={4,5};
    
    struct complex *ptr =&c1;
printf("real part =%d \n",c1.real);
printf("imaginary %d",ptr-> img);
}
