import codecs
a = "en"
b = "no"
lcode = "no"


k=codecs.open('data/OpenSubtitles2016.{}-{}.{}'.format(a, b, lcode), 'r', 'utf-8').read()
print(k.count("\n"))
p=k.split("\n")
print(len(p))
print(len(k.splitlines()))