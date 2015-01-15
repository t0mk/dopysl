# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__license__ = 'MIT'

import manager

DO_API_CREDENTIALS = """
Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.
If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

Manager().new_droplet('new_vm', '512mb', 'lamp', 'ams2')

If you use APIv1 you first need to get ID of those.

If you want to use APIv2, you need to find out the api token from:
https://cloud.digitalocean.com/settings/applications

and you shoud set it as envvar:
export DO_API_TOKEN=...

If you still want to use APIv1 you need to define client ID and API key.
!!! API key for v1 is different than API token for v2 !!!
Find it out from:
https://cloud.digitalocean.com/api_accessA

And set it as:
export DO_CLIENT_ID=...
export DO_API_KEY=...
"""


def usage():
    print DO_API_CREDENTIALS
    sys.exit(1)


class Proxy(object):
    _manager = None
    def __new__(cls, *args, **kwargs):
        if not cls._manager:
            if os.environ.get('DO_API_TOKEN'):
                api_token = os.environ.get('DO_API_TOKEN')
                cls._manager = manager.DoManager(None, api_token, 2)
            else:
                # we assume APIv1
                client_id = os.environ.get('DO_CLIENT_ID') or usage()
                api_key = os.environ.get('DO_API_KEY') or usage()
                cls._manager = manager.DoManager(client_id, api_key, 1)
        return cls._manager

