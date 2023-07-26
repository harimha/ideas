class Parent1:
    def __init__(self):
        self.var1 = "Parent1"

    def method1(self):
        print("Method 1 from Parent1")


class Parent2:
    def __init__(self):
        self.var2 = "Parent2"

    def method2(self):
        print("Method 2 from Parent2")


class Child(Parent1, Parent2):
    def __init__(self):
        # Parent1의 __init__ 메서드 호출
        Parent1.__init__(self)
        Parent2.__init__(self)

    def method3(self):
        print("Method 3 from Child")


child = Child()
print(child.var2)  # Output: Parent1