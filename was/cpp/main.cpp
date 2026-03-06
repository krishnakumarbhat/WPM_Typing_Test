#include <iostream>
using namespace std;

int main()
{

    int marks[] = {23, 45, 56, 89};
    for (int i = 0; i < 4; i++)
    {
        // cout << "The value of marks " <<  (&i)<< " is " << &marks[i] << endl;
        // cout << &marks[5] ;
    }

    // while (int i == '\n'){
    //     cout << "The value of marks " <<  (&i)<< " is " << &marks[i] << endl;
    //     i = i+1;
    // }
    //  cout << &marks ;
    //  int* p = marks;
     
    // for (int i = 0; i < 95; i++)
    // {
    //     cout << *p << endl;
    //     p++;

    // }

    int* p = marks;
cout<<"The value of marks[0] is "<<*p<<endl;

    cout<<"The value of *p is "<<*p<<endl;
    cout<<"The value of *(p+1) is "<<*(p+1)<<endl;
    cout<<"The value of *(p+2) is "<<*(p+2)<<endl;
    cout<<"The value of *(p+3) is "<<*(p+3)<<endl; 
    cout<<"The value of *(p+56) is "<<*(p+56)<<endl; 

       cout<<*(p++)<<endl;
    cout<<*(++p)<<endl;

}