import threading
import time

local_data = threading.local()


def decorator(fun):
    def wrapper(*args):
        local_data.g = threading.currentThread()
        return fun(*args)

    return wrapper


# @decorator
def fun1():
    print("fun1 running...")
    time.sleep(1)
    local_data.g = 'hello'
    print("local data: ", local_data.g)


# @decorator
def fun2():
    print("fun2 running...")
    local_data.g = 'world'
    time.sleep(2)
    print("local data: ", local_data.g)


th1 = threading.Thread(target=fun1)
th2 = threading.Thread(target=fun2)

# th1.start()
# th2.start()


# import datetime
#
# a = datetime.datetime.utcnow()
# print(a)
a = {}
b = a.pop('h', 1)
print(b, type(b))