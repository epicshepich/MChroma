class Test:
    def __init__(self):
        self.a = "a"
        self.b = False
        self.c = [1,2,3]

    def method(self):
        print("test")

test = Test()
#print(test.__dict__)

test.__dict__["a"] = "A"
#print(test.a)

f,g=[1,2]
#print(f)

result = "\x18"
results = ["Test","\x18"]
#print(result in "\x18")


#xkcd_colors = list(seaborn.xkcd_rgb.keys())
#List of xkcd colors for coloring clusters on scatter plot.

#print(xkcd_colors)


#print(colors)

def test(**kwargs):
    print(kwargs)

#test(a="a",b="b")
#print("-1".isnumeric())

d = {"a","\x19"}
#print("a" in d

print("-12".isnumeric())
