"""
Easing functions are smooth, real valued functions defined over the range
[0, 1].  Behavior outside this interval is not specified.  See
http://robertpenner.com/easing/ for more info.  Each of these functions takes a
single float in [0, 1] and returns a float in [0, 1].

=====================   =============   ============    ===================
function type           in function     out function    in-out function
=====================   =============   ============    ===================
linear                  linear          linear          linear
2nd degree polynomial   in_p2           out_p2          in_out_p2
3rd degree polynomial   in_p3           out_p3          in_out_p3
4th degree polynomial   in_p4           out_p4          in_out_p4
5th degree polynomial   in_p5           out_p5          in_out_p5
circular                in_circ         out_circ        in_out_circ
sin                     in_sin          out_sin         in_out_sin
exp                     in_exp          out_exp         in_out_exp
=====================   =============   ============    ===================

"""
import math


def linear(t):
    return t


def in_p2(t):
    return t * t


def out_p2(t):
    return 1 - (1 - t) * (1 - t)


def in_out_p2(t):
    return in_p2(2 * t) / 2 if (t < 0.5) else 1 - in_p2(2 * (1 - t)) / 2


def in_p3(t):
    return t * t * t


def out_p3(t):
    return 1 - in_p4(1 - t)


def in_out_p3(t):
    return in_p3(2 * t) / 2 if (t < 0.5) else 1 - in_p3(2 * (1 - t)) / 2


def in_p4(t):
    return t * t * t * t


def out_p4(t):
    return 1 - in_p4(1 - t)


def in_out_p4(t):
    return in_p4(2 * t) / 2 if (t < 0.5) else 1 - in_p4(2 * (1 - t)) / 2


def in_p5(t):
    return t * t * t * t * t


def out_p5(t):
    return 1 - in_p5(1 - t)


def in_out_p5(t):
    return in_p5(2 * t) / 2 if (t < 0.5) else 1 - in_p5(2 * (1 - t)) / 2


def in_circ(t):
    return 1 - math.sqrt(1 - t * t)


def out_circ(t):
    return 1 - in_circ(1 - t)


def in_out_circ(t):
    return in_circ(2.0 * t) / 2.0 if (t < 0.5) else 1 - in_circ(2 * (1 - t)) / 2


def in_sin(t):
    return 1 - math.cos(t * math.pi / 2)


def out_sin(t):
    return math.sin(t * math.pi / 2)


def in_out_sin(t):
    return 0.5 * (1 - math.cos(t * math.pi))


def in_exp(alpha):
    if alpha == 0.0:
        return lambda t: t
    else:
        k = 1.0 / (math.exp(alpha) - 1)
        return lambda t: (math.exp(alpha * t) - 1) * k


def out_exp(alpha):
    if alpha == 0.0:
        return lambda t: t
    else:
        k = 1.0 / (math.exp(alpha) - 1)
        return lambda t: 1 - (math.exp(alpha * (1 - t)) - 1) * k


def in_out_exp(alpha):
    if alpha == 0.0:
        return lambda t: t
    f = in_exp(alpha)

    def _(t):
        if t < 0.5:
            return f(2 * t) * 0.5
        else:
            return 1 - f(2.0 * (1 - t)) * 0.5

    return _
