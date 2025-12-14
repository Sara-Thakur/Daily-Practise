#include<stdio.h>
float t(float c);
float main(){
    printf("fahrenheit %.2f",t(39));
    return 0; 
}
float t(float c){
    if (c==0){
        return 32; }
     float f;
     f=c*(9.0/5.0)+32;
     return f;
}