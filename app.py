import logging
import os
from datetime import datetime, timedelta
import json
import sys

from flask import Flask, request, make_response, jsonify
from raven.contrib.flask import Sentry
import app_config

from rq import Queue
from rq.job import Job
from worker import conn

from tasks import run_scripts
from handlers import parse_post

app = Flask(__name__)
app.config.from_object(app_config)

app.url_map.strict_slashes = False

sentry = Sentry(app, dsn=app_config.SENTRY_DSN)

q = Queue(connection=conn)

# expects GeoJSON object as a string
# client will need to use JSON.stringify() or similar

class AppError(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidUsage(AppError):
    status_code = 400
    pass

class ServerError(AppError):
    status_code = 500
    pass

class PayloadException(InvalidUsage):
    pass

@app.errorhandler(AppError)
def handle_payload_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/hooks/<site_type>/<branch_name>', methods=['POST'])
def execute(site_type, branch_name):
    post = request.get_json()

    content_type = request.headers.get('Content-Type')

    if content_type != 'application/json':
        raise ServerError('handling {content_type} is not implemented'.format(content_type=content_type),
                          status_code=501)
        
    resp = {'status': 'ok'}
    
    post, hostname = parse_post(post, branch_name)

    giturl = 'git@{server}:{owner}/{repo}.git'\
                 .format(server=app_config.GH_SERVER,
                         owner=post['owner'],
                         repo=post['repo'])

    # source
    source = '{temp}/{owner}/{repo}/{branch}/code'\
                 .format(temp=app_config.TEMP,
                         owner=post['owner'],
                         repo=post['repo'],
                         branch=post['branch'])

    build = '{temp}/{owner}/{repo}/{branch}/site'\
                .format(temp=app_config.TEMP,
                        owner=post['owner'],
                        repo=post['repo'],
                        branch=post['branch'])

    venv_bin_dir = os.path.dirname(sys.executable)
        
    if hostname and app_config.CONFIG_NGINX:
        q.enqueue_call(func=run_scripts, args = (app_config.NGINX_SCRIPT, [hostname, post['repo'], venv_bin_dir]))
        
    if post:
        script_args = [post['repo'], post['branch'], post['owner'], giturl, source, build]
        try:
            scripts = app_config.SCRIPTS[site_type]
        except KeyError:
            raise ServerError("No script file defined for '{0}' in config.".format(site_type),
                        status_code=501)
        else:
            job = q.enqueue_call(
                func=run_scripts, args = (scripts, script_args), result_ttl = 5000
            )

    response = make_response(json.dumps(resp), 202)
    response.headers['Content-Type'] = 'application/json'
    return response

# INIT
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
