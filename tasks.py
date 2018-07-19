import subprocess

from app_config import SENTRY_DSN, REDIS_QUEUE_KEY

from raven import Client

sentry = Client(SENTRY_DSN)

def run_scripts(scripts, args):
    for s in scripts:
        try:
            subprocess.check_call([s] + args)
        except subprocess.CalledProcessError as e:
            print('EXCEPTION', e)
            sentry.captureException()
