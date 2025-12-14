 #include <stdio.h>
 int sum (int n);
 int main(){
    int n;
    printf("enter a number");
    scanf("%d",&n);
    int s=sum(n);
    printf("sum of digits %d\n",s);
    return 0;
 }
 int sum (int n){
    int sum=0;
    while (n!=0){
      sum+=n%10;
      n/=10;
    }return sum;
 }