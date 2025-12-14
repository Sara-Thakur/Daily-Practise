#include<stdio.h>
void pHW(int c);
int main(){
    pHW (5);
    return 0;
}
void pHW (int c){
    if (c==0){
        return;}
    printf("helloworld\n");
    pHW(c-1);

}