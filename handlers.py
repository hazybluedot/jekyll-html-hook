import urllib.request
import json
import app_config

def parse_post(post, branch):

    if 'ref' not in post.keys():
        return []

    # Parse webhook data for internal variables
    post['repo'] = post['repository']['name']
    post['branch'] = post['ref'].replace('refs/heads/', '')
    post['owner'] = post['repository']['owner']['name']

    # End early if not permitted account
    if post['owner'] not in app_config.ACCOUNTS:
        raise PayloadException('Account {user} not permitted'.format(user=post['owner']),
                               status_code=403)

    # End early if not permitted branch

    if post['branch'] != branch:
        raise PayloadException('Branch {branch} not permitted'.format(branch=post['branch']),
                               status_code=403)


    hostname = None
    if app_config.CONFIG_NGINX:
        cname_url = 'https://api.github.com/repos/{owner}/{repo}/contents/CNAME?access_token={token}'
        cname_url = cname_url.format(owner=post['owner'],
                                     repo=post['repo'],
                                     token=app_config.GH_TOKEN)

        try:
            cname_resp = urllib.request.urlopen(cname_url)
        except urllib.error.HTTPError as e:
            raise PayloadException('{url}: {reason}'.format(url=cname_url, reason=e.reason),
                                   status_code=e.code)
        else:
            data = cname_resp.read()
            encoding = cname_resp.info().get_content_charset('utf-8')
            resp = json.loads(data.decode(encoding))
            
            download_url = resp['download_url']

            cname = urllib.request.urlopen(download_url)
            
            hostname = cname.read()
                
    return (post, hostname)
