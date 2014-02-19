def human_readable_duration(seconds):
    """Converts a large number of seconds to a human readable tuple.

    :returns: (int, "unit of time")

    """
    if round(seconds / 60. / 60. / 24. / 7. / 52.) > 2:
        t = (seconds / 60. / 60. / 24. / 7. / 52., 'years')
    elif round(seconds / 60. / 60. / 24. / 7. / (52. / 12.)) > 2:
        t = (seconds / 60. / 60. / 24. / 7. / (52. / 12.), 'months')
    elif round(seconds / 60. / 60. / 24. / 7.) > 2:
        t = (seconds / 60. / 60. / 24. / 7., 'weeks')
    elif round(seconds / 60. / 60. / 24.) > 2:
        t = (seconds / 60. / 60. / 24., 'days')
    elif round(seconds / 60. / 60.) > 2:
        t = (seconds / 60. / 60., 'hours')
    elif round(seconds / 60.) > 2:
        t = (seconds / 60., 'minutes')
    else:
        t = (seconds, 'seconds')

    # convert to an int
    value = int(round(t[0]))

    # drop plurality on the unit if appropriate
    units = t[1] if value != 1 else t[1][:-1]

    return (value, units)
