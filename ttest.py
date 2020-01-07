wake_words = ['video helper', 'videohelper']
clip_words = ['start clip', 'end clip']
marker_words = ['add mark', 'add marks']
phrases = dict(wake_words=wake_words,
               clip_words=clip_words,
               marker_words=marker_words)
import functools
import operator
import itertools

print(wake_words + clip_words)

print(phrases.values())
print(functools.reduce(operator.concat, phrases.values()))

# sum(phrases.values())
# sum(['foo', 'bar'], '')
# [''.join((['foo', 'bar'], ['foo', 'bar']))]
a = "".join(['foo', 'bar'])
print(a)

phrases = list(itertools.chain.from_iterable(phrases.values()))
print(phrases)