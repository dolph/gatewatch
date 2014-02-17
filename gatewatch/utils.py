def human_readable_duration(seconds):
    """Converts a large number of seconds to a human readable tuple.

    :returns: (int, "unit of time")

    """
    if seconds / 60. / 60. / 24. / 7. / 52. > 1:
        t = (seconds / 60. / 60. / 24. / 7. / 52., 'years')
    elif seconds / 60. / 60. / 24. / 7. / (52. / 12.) > 1:
        t = (seconds / 60. / 60. / 24. / 7. / (52. / 12.), 'months')
    elif seconds / 60. / 60. / 24. / 7. > 1:
        t = (seconds / 60. / 60. / 24. / 7., 'weeks')
    elif seconds / 60. / 60. / 24. > 1:
        t = (seconds / 60. / 60. / 24., 'days')
    elif seconds / 60. / 60. > 1:
        t = (seconds / 60. / 60., 'hours')
    elif seconds / 60. > 1:
        t = (seconds / 60., 'minutes')
    else:
        t = (seconds, 'seconds')

    # convert to an int
    value = int(round(t[0]))

    # drop plurality on the unit if appropriate
    units = t[1] if value != 1 else t[1][:-1]

    return (value, units)
