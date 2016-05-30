import random


def weighted_choice(items):
    total = sum(i[1] for i in items if i[1] >= 0)
    goal = random.uniform(0, total)

    for value, weight in items:
        if weight >= 0:
            goal -= weight
            if goal <= 0:
                return value