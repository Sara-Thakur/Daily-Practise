#include<stdio.h>

int countOdd(int arr[],int n);

int main(){
    
    int arr[]={1,2,3,4,5,6,9,12};
    printf("%d",countOdd(arr,8));
   

    return 0;
    }
int countOdd(int arr[],int n){
    int count=0;
    int i;
    for (int i=0;i<n;i++){
        if (arr[i] % 3 == 0){
        count++;}
    }

    return count;
}