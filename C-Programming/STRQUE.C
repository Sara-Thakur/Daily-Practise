#include<stdio.h>
#include<string.h>
struct vector{
    int x;
    int y;
};
void summ(struct vector v1,struct vector v2,struct vector sum);

int main (){
    struct vector v1 ={5,10};
    struct vector v2={2,6};
    struct vector sum={0};
    summ(v1,v2,sum);
    return 0;
}
void summ(struct vector v1,struct vector v2,struct vector sum){
    sum.x= v1.x+v2.x;
    sum.y= v1.y + v2.y;
    printf ("sum of vectors in x %d \n",sum.x);
    printf("sum in y %d\n",sum.y);

}