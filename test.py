class Test:
    def __init__(self):
        self.a = "a"
        self.b = False
        self.c = [1,2,3]

    def method(self):
        print("test")

test = Test()
print(test.__dict__)

test.__dict__["a"] = "A"
print(test.a)

f,g=[1,2]
print(f)
