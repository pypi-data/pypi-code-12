round_number = lambda x: int(round(abs(x)))


def get_percent_change(new_value, old_value):
    if not old_value and not new_value:
        return 0
    if not old_value:
        sign = 1 if new_value > 0 else -1
        return sign * float('inf')
    change_difference = new_value - old_value
    change_ratio = change_difference / float(old_value)
    return 100 * change_ratio


def define_normalize(xs, (y_min, y_max)):
    x_min = min(xs)
    x_max = max(xs)
    x_width = (x_max - x_min) or 1
    y_width = (y_max - y_min) or 1

    def normalize(x):
        unit_x = (x - x_min) / float(x_width)
        return (unit_x * y_width) + y_min

    return normalize
