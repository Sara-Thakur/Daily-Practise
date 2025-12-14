#include<stdio.h>
int reverse (int arr[],int n);
int main(){
    int arr[]={1,2,3,4,5};
    reverse(arr,5);
    return 0;
    
}
int reverse(int arr[],int n){
    for(int i=0;i<n/2;i++){
        int fv=arr[i];
        int sv=arr[n-i-1];
        arr[i]=sv;
        arr[n-i-1]=fv;
    }
    for(int i=0;i<n;i++){
        printf("%d\t",arr[i]);
    }
}