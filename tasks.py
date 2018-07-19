import subprocess

from app_config import SENTRY_DSN, REDIS_QUEUE_KEY

from raven import Client

sentry = Client(SENTRY_DSN)

def run_scripts(scripts, args):
    build, publish = scripts

    try:
        subprocess.check_call([build] + args)
    except subprocess.CalledProcessError as e:
        print('EXCEPTION', e)
        sentry.captureException()

    try:
        subprocess.check_call([publish] + args)
    except subprocess.CalledProcessError as e:
        print('EXCEPTION', e)
        sentry.captureException()
