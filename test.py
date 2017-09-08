# from translate import Trans
#
# trans = Trans("en", "hu")
#
# print(trans("place", 10))
a, b= "en", "hu"
source_lang = "en"
target_lang="hu"
import pickle
x_to_ys = pickle.load(open('outputs/{}-{}/{}-{}.trans.pkl'.format(a, b, source_lang, target_lang), 'rb'))
print(x_to_ys)