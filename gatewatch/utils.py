def human_readable_duration(seconds):
    """Converts a large number of seconds to a human readable tuple.

    :returns: (int, "unit of time")

    """
    if round(seconds / 60. / 60. / 24. / 7. / 52.) > 1.5:
        t = (seconds / 60. / 60. / 24. / 7. / 52., 'yrs')
    elif round(seconds / 60. / 60. / 24. / 7.) > 1.5:
        t = (seconds / 60. / 60. / 24. / 7., 'wks')
    elif round(seconds / 60. / 60. / 24.) > 1.5:
        t = (seconds / 60. / 60. / 24., 'days')
    elif round(seconds / 60. / 60.) > 1.5:
        t = (seconds / 60. / 60., 'hrs')
    elif round(seconds / 60.) > 1.5:
        t = (seconds / 60., 'mins')
    else:
        t = (seconds, 'secs')

    # convert to an int
    value = int(round(t[0]))

    # drop plurality on the unit if appropriate
    units = t[1] if value != 1 else t[1][:-1]

    return (value, units)
