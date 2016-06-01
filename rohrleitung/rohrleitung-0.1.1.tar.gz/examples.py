from functools import partial
# pip install toolz
from toolz.curried import interpose

from rohrleitung import Pipeline, L


def three_n_plus_one(n):
    if n % 2:
        return 3 * n + 1
    else:
        return n / 2


@L
def collatz_length(n, l=0):
    if int(n) < 1:
        raise ValueError('Nope')
    if n == 1:
        return l
    else:
        # L changes call signatures of decorated function, so in recursive ones
        # you have to adapt.
        return collatz_length.__wrapped__(three_n_plus_one(n), l + 1)

# building pipelines in a programmatic way, without immediately executing them
# standard list manipulation can change pipeline on the fly
pipeline = [
    partial(filter, lambda x: x % 2),  # Standard python's filter function
    lambda y: (2 * x for x in y),      # Like using L, but manually
    L(lambda x: x ** 3),               # Using L helper function
    collatz_length,
]
pipeline.append(interpose('a'))
print(list(Pipeline(pipeline, range(10))))

a = Pipeline([L(lambda x: 2 * x), L(lambda x: x + 1), L(lambda x: x ** 2)])
for i, k in enumerate(a(range(3))):
    print("(2x+1)^2, x={}: {}".format(i, k))

# With toolz' curried filter function we don't need partial
from toolz.curried import filter
newpipeline = [
    collatz_length,
    filter(lambda x: not(x % 2)),
    L(lambda x: bin(x)),
    L(lambda x: x.count('1'))
]
p1 = Pipeline(newpipeline)
for i in p1(range(1, 10)):
    print(i)

# Reuse same pipeline
for i in p1(range(1, 3)):
    print(i)

# Or modify it, then use again
p1.pipeline.insert(2, L(lambda x: x + 1))
for i in p1(range(1, 10)):
    print(i)

p2 = Pipeline(pipeline)
p3 = 2 * (p2 + [L(lambda x: int(str(x), 16))]) + p1
# Alternativly 2 * p2 | p1 if you prefer shell syntax
for i in p3(range(1, 10)):
    print(i)

# Slicing and cutting pipelines on the fly
for i in p1[1:4:2](range(10)):
    print(i)
