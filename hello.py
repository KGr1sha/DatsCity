import cython as c

def say_hello(name):
    print(factorial(3));

def factorial(number: c.int):
    ans: c.int = 1;
    i: c.int;
    for i in range(2, number+1):
        ans *= i;
    return ans 
