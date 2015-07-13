# -*- coding: utf-8 -*-

__version__ = '0.0.3'
__license__ = 'MIT'


import inspect
import json
import os
import requests

API_ENDPOINT = 'https://api.digitalocean.com/v2'
DEBUG = False

DO_API_CREDENTIALS = """
Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.
If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

Manager().new_droplet('new_vm', '512mb', 'lamp', 'ams2')

If you want to use APIv2, you need to find out the api token from:
https://cloud.digitalocean.com/settings/applications

and you shoud set it as envvar:
export DO_API_TOKEN=...

"""


def usage():
    print DO_API_CREDENTIALS
    sys.exit(1)

class DoError(RuntimeError):
    pass

import httplib
import urllib

def print_debug():
    """ this will print HTTP requests sent """
    # http://stackoverflow.com/questions/20658572/
    # python-requests-print-entire-http-request-raw
    global DEBUG
    DEBUG = True
    old_send= httplib.HTTPConnection.send
    def new_send( self, data ):
        print urllib.unquote(data).decode('utf8')
        return old_send(self, data)
    httplib.HTTPConnection.send = new_send

def get_id_by_attr(res_pattern, res_list, attr='name'):
    result_list = [i['id'] for i in res_list if i[attr] == res_pattern]
    if len(result_list) > 1:
        raise DoError("name %s is valid for more ids: %s " %
                      (res_pattern, result_list))
    if len(result_list) == 0:
        raise DoError("no resources found for %s, whole list: %s " %
                      (res_pattern, res_list))
    return result_list[0]


class DoManager(object):

    def __init__(self, client_id, api_key, api_version=1):
        self.api_endpoint = API_ENDPOINT
        self.client_id = client_id
        self.api_key = api_key
        self.api_version = int(api_version)

    def all_active_droplets(self):
        json_out = self.request('/droplets/')
        return json_out['droplets']

    def get_key_id(self, key_name):
        return get_id_by_attr(key_name, self.all_ssh_keys())

    def new_droplet(self, name, size, image, region,
            ssh_keys, private_networking=False,
            backups_enabled=False):
        params = {
            'name': name,
            'size': size,
            'image': image,
            'region': region,
            'private_networking': None,
            'user_data': None,
            'ipv6': True,
            'backups': backups_enabled,
        }
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        params['ssh_keys'] = ssh_keys
        json_out = self.request('/droplets', params=params, method='POST')
        return json_out['droplet']

    def show_droplet(self, id):
        json_out = self.request('/droplets/%s' % id)
        return json_out['droplet']

    def droplet_v2_action(self, id, type, params={}):
        params = {
            'type': type
        }
        json_out = self.request('/droplets/%s/actions' % id, params=params, method='POST')
        return json_out

    def reboot_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'reboot')
        json_out.pop('status', None)
        return json_out

    def power_cycle_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'power_cycle')
        json_out.pop('status', None)
        return json_out

    def shutdown_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'shutdown')
        json_out.pop('status', None)
        return json_out

    def power_off_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'power_off')
        json_out.pop('status', None)
        return json_out

    def power_on_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'power_on')
        json_out.pop('status', None)
        return json_out

    def password_reset_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'password_reset')
        json_out.pop('status', None)
        return json_out

    def resize_droplet(self, id, size_id):
        params = {'size': size_id}
        json_out = self.droplet_v2_action(id, 'resize', params)
        json_out.pop('status', None)
        return json_out

    def snapshot_droplet(self, id, name):
        params = {'name': name}
        json_out = self.droplet_v2_action(id, 'snapshot', params)
        json_out.pop('status', None)
        return json_out

    def restore_droplet(self, id, image_id):
        params = {'image': image_id}
        json_out = self.droplet_v2_action(id, 'restore', params)
        json_out.pop('status', None)
        return json_out

    def rebuild_droplet(self, id, image_id):
        params = {'image': image_id}
        json_out = self.droplet_v2_action(id, 'rebuild', params)
        json_out.pop('status', None)
        return json_out

    def enable_backups_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'enable_backups')
        json_out.pop('status', None)
        return json_out

    def disable_backups_droplet(self, id):
        json_out = self.droplet_v2_action(id, 'disable_backups')
        json_out.pop('status', None)
        return json_out

    def rename_droplet(self, id, name):
        params = {'name': name}
        json_out = self.droplet_v2_action(id, 'rename', params)
        json_out.pop('status', None)
        return json_out

    def destroy_droplet(self, id, scrub_data=True):
        json_out = self.request('/droplets/%s' % id, method='DELETE')
        json_out.pop('status', None)
        return json_out

#regions==========================================
    def all_regions(self):
        json_out = self.request('/regions/')
        return json_out['regions']

#images==========================================
    def all_images(self, filter='global'):
        params = {'filter': filter}
        json_out = self.request('/images/', params)
        return json_out['images']

    def image_v2_action(self, id, type, params={}):
        params = {
            'type': type
        }
        json_out = self.request('/images/%s/actions' % id, params=params, method='POST')
        return json_out

    def show_image(self, image_id):
        params= {'image_id': image_id}
        json_out = self.request('/images/%s' % image_id)
        return json_out['image']

    def destroy_image(self, image_id):
        self.request('/images/%s' % id, method='DELETE')
        return True

    def transfer_image(self, image_id, region_id):
        params = {'region': region_id}
        json_out = self.image_v2_action(id, 'transfer', params)
        json_out.pop('status', None)
        return json_out

#ssh_keys=========================================
    def all_ssh_keys(self):
        json_out = self.request('/account/keys')
        return json_out['ssh_keys']

    def new_ssh_key(self, name, pub_key):
        params = {'name': name, 'public_key': pub_key}
        json_out = self.request('/account/keys', params, method='POST')
        return json_out['ssh_key']

    def show_ssh_key(self, key_id):
        json_out = self.request('/account/keys/%s/' % key_id)
        return json_out['ssh_key']

    def edit_ssh_key(self, key_id, name, pub_key):
        params = {'name': name} # v2 API doesn't allow to change key body now
        json_out = self.request('/account/keys/%s/' % key_id, params, method='PUT')
        return json_out['ssh_key']

    def destroy_ssh_key(self, key_id):
        self.request('/account/keys/%s' % key_id, method='DELETE')
        return True

#sizes============================================
    def sizes(self):
        json_out = self.request('/sizes/')
        return json_out['sizes']

#domains==========================================
    def all_domains(self):
        json_out = self.request('/domains/')
        return json_out['domains']

    def new_domain(self, name, ip):
        params = {
                'name': name,
                'ip_address': ip
            }
        json_out = self.request('/domains', params=params, method='POST')
        return json_out['domain']

    def show_domain(self, domain_id):
        json_out = self.request('/domains/%s/' % domain_id)
        return json_out['domain']

    def destroy_domain(self, domain_id):
        self.request('/domains/%s' % domain_id, method='DELETE')
        return True

    def all_domain_records(self, domain_id):
        json_out = self.request('/domains/%s/records/' % domain_id)
        return json_out['domain_records']

    def new_domain_record(self, domain_id, record_type, data, name=None, priority=None, port=None, weight=None):
        params = {'data': data}

        params['type'] = record_type
        if name: params['name'] = name
        if priority: params['priority'] = priority
        if port: params['port'] = port
        if weight: params['weight'] = weight

        json_out = self.request('/domains/%s/records/' % domain_id, params, method='POST')
        return json_out['record']

    def show_domain_record(self, domain_id, record_id):
        json_out = self.request('/domains/%s/records/%s' % (domain_id, record_id))
        return json_out['domain_record']

    def edit_domain_record(self, domain_id, record_id, record_type, data, name=None, priority=None, port=None, weight=None):
        params['name'] = name # API v.2 allows only record name change
        json_out = self.request('/domains/%s/records/%s' % (domain_id, record_id), params, method=PUT)
        return json_out['domain_record']

    def destroy_domain_record(self, domain_id, record_id):
        self.request('/domains/%s/records/%s' % (domain_id, record_id), method='DELETE')
        return True

#events(actions in v2 API)========================
    def show_all_actions(self):
        json_out = self.request('/actions')
        return json_out['actions']

    def show_action(self, action_id):
        json_out = self.request('/actions/%s' % event_id)
        return json_out['action']

    def show_event(self, event_id):
        return show_action(self,event_id)

#low_level========================================
    def request(self, path, params={}, method='GET'):
        if not path.startswith('/'):
            path = '/'+path
        url = self.api_endpoint+path
        headers = { 'Authorization': "Bearer %s" % self.api_key }
        headers['Content-Type'] = 'application/json'
        resp = self.request_v2(url, params=params, headers=headers,
                               method=method)
        return resp


    def request_v2(self, url, headers={}, params={}, method='GET'):
        params = json.dumps(params)

        try:
            if method == 'POST':
                resp = requests.post(url, data=params, headers=headers, timeout=60)
                json_out = resp.json()
            elif method == 'DELETE':
                resp = requests.delete(url, headers=headers, timeout=60)
                json_out = {'status': resp.status_code}
            elif method == 'PUT':
                resp = requests.put(url, headers=headers, params=params, timeout=60)
                json_out = resp.json()
            elif method == 'GET':
                resp = requests.get(url, headers=headers, params=params, timeout=60)
                json_out = resp.json()
            else:
                raise DoError('Unsupported method %s' % method)

        except ValueError:  # requests.models.json.JSONDecodeError
            raise ValueError("The API server doesn't respond with a valid json_out")
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e)
        
        if DEBUG:
            print resp.status_code
            print json.dumps(json_out, sort_keys=True, indent=4)

        if resp.status_code != requests.codes.ok:
            if json_out:
                if 'error_message' in json_out:
                    raise DoError(json_out['error_message'])
                elif 'message' in json_out:
                    raise DoError(json_out['message'])
            # The JSON reponse is bad, so raise an exception with the HTTP status
            resp.raise_for_status()

        if json_out.get('id') == 'not_found':
            raise DoError(json_out['message'])

        return json_out


class Proxy(object):
    _manager = None
    def __new__(cls, *args, **kwargs):
        if not cls._manager:
            if os.environ.get('DO_API_TOKEN'):
                api_token = os.environ.get('DO_API_TOKEN')
                cls._manager = DoManager(None, api_token, 2)
        return cls._manager


def init():
    """ checks if credentials are present and initalizes the module """
    manager = Proxy()

    current_module = __import__(__name__)
    # Following registers all the methods of DoManager to current namespace
    # so that we can call straight list
    # dopysl.init()
    # dopysl.all_active_droplets()
    for name, method in inspect.getmembers(manager, inspect.ismethod):
        if name != "__init__":
            setattr(current_module, name, method)



