import math

def linear(t):
    return t

def inP2(t):
    return t * t

def outP2(t):
    return 1 - (1 - t) * (1 - t)

def inOutP2(t):
    return inP2(2 * t) / 2 if (t < 0.5) else 1 - inP2(2 * (1 - t)) / 2

def inP3(t):
    return t * t * t

def outP3(t):
    return 1 - inP4(1 - t)

def inOutP3(t):
    return inP3(2 * t) / 2 if (t < 0.5) else 1 - inP3(2 * (1 - t)) / 2

def inP4(t):
    return t * t * t * t

def outP4(t):
    return 1 - inP4(1 - t)

def inOutP4(t):
    return inP4(2 * t) / 2 if (t < 0.5) else 1 - inP4(2 * (1 - t)) / 2

def inP5(t):
    return t * t * t * t * t

def outP5(t):
    return 1 - inP5(1 - t)

def inOutP5(t):
    return inP5(2 * t) / 2 if (t < 0.5) else 1 - inP5(2 * (1 - t)) / 2

def inCirc(t):
    return 1 - math.sqrt(1 - t * t)

def outCirc(t):
    return 1 - inCirc(1 - t)

def inOutCirc(t):
    return inCirc(2.0 * t) / 2.0 if (t < 0.5) else 1 - inCirc(2 * (1 - t)) / 2

def inSin(t):
    return 1 - math.cos(t * math.pi / 2)

def outSin(t):
    return math.sin(t * math.pi / 2)

def itOutSin(t):
    return 0.5 * (1 - math.cos(t * math.pi))

def inExp(alpha):
    if alpha == 0.0:
        return lambda t: t
    else:
        k = 1.0/(math.exp(alpha) - 1)
        return lambda t: (math.exp(alpha * t) - 1) * k

def outExp(alpha):
    if alpha == 0.0:
        return lambda t: t
    else:
        k = 1.0/(math.exp(alpha) - 1)
        return lambda t: 1 - (math.exp(alpha * (1 - t)) - 1) * k

def inOutExp(alpha):
    if alpha == 0.0:
        return lambda t: t
    f = inExp(alpha)
    def _(t):
        if t < 0.5:
            return f(2 * t) * 0.5
        else:
            return 1 - f(2.0 * (1 - t)) * 0.5
    return _

