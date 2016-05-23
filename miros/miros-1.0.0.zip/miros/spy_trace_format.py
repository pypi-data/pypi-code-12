
def s( time, state, event, payload, chart=None ):
  if payload is None:
    return "[%s] %s: %s" % (time, event, state)
  else:
    return "[%s] %s: %s:: %s" % (time, event, state, payload)

def t( time, state_n_0, state_n_1, event, payload, chart=None ):
  if payload is None:
    return "[%s] %s: %s->%s" % (time, event, state_n_0, state_n_1)
  else:
    return "[%s] %s: %s->%s:: %s" % (time, event, state_n_0, state_n_1, payload)


def s_with_chart( time, state, event, payload, chart ):
  if payload is None:
    return "[%s](%s) %s: %s" % (time, chart, event, state)
  else:
    return "[%s](%s) %s: %s:: %s" % (time, chart, event, state, payload)

def t_with_chart( time, state_n_0, state_n_1, event, payload, chart ):
  if payload is None:
    return "[%s](%s) %s: %s->%s" % (time, chart, event, state_n_0, state_n_1)
  else:
    return "[%s](%s) %s: %s->%s:: %s" % (time, chart, event, state_n_0, state_n_1, payload)
