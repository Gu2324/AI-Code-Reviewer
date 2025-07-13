class MyObject:
    def __init__(self, value):
        self.value = value
obj1 = MyObject(1)
obj2 = MyObject(1)
if obj1 == obj2:
    print("Objects are equal")