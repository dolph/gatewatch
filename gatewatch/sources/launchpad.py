import os

from launchpadlib import launchpad

from gatewatch import backend
from gatewatch import tasks


NAME = 'Dolph Mathews'
LP_INSTANCE = 'production'
CACHE_DIR = os.path.expanduser('~/.launchpadlib/cache/')


@tasks.app.task
def next_milestone_date(project):
    client = launchpad.Launchpad.login_anonymously(
        NAME, LP_INSTANCE, CACHE_DIR)
    project = client.projects[project]

    dates = [x.date_targeted for x in project.active_milestones
             if x.date_targeted is not None]

    next_milestone_date = sorted(dates)[0]
    backend.write(next_milestone_date=str(next_milestone_date))

    return next_milestone_date
