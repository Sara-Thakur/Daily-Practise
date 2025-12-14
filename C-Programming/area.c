#include<stdio.h>
int sq(int n);
float circle(int n);
int rect(int a, int b);
int main(){
    char c;
    printf("area of:s for square,c fir circle, r for rectangle::");
    scanf("%c",&c);
    
    if (c =='s'){
        int n;
        printf("side ");
        scanf("%d",&n);
        printf("%d",sq(n));
     }
     else if (c=='c'){
        int n;
        printf("radius ");
        scanf("%d",&n);
        printf("%.2f",circle(n));
     }
     else if (c=='r'){
        int a,b;
        printf("length ");
        scanf("%d",&a);
        printf("breadth ");
        scanf("%d",&b);
        printf("rect area %d",rect(a,b));}
    else{
        printf("invalid");
    }

    return 0 ; }
int sq(int n){
   return n*n;}
float circle(int n){
    return n*n*3.14;}
int rect(int a,int b){
    return a*b;
}
    