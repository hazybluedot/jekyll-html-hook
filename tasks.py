import logging
log = logging.getLogger('app.task')

import subprocess

from app_config import SENTRY_DSN

from raven import Client

sentry = Client(SENTRY_DSN)

def run_scripts(scripts, args):
    for s in scripts:
        try:
            subprocess.check_call([s] + args)
        except subprocess.CalledProcessError as e:
            log.error('EXCEPTION: {}'.format(e.message))
            sentry.captureException()
