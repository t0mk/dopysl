#!/usr/bin/env python3

import pprint
import argparse
import inspect
import json
import os
import requests
import argh
import subprocess
import urllib.parse

API_ENDPOINT = 'https://api.digitalocean.com/v2'
DEBUG = False

DO_API_TOKEN = os.environ.get('DO_API_TOKEN')
DO_KEYPAIR_ID = os.environ.get('DO_KEYPAIR_ID')
DO_KEY = os.environ.get('DO_KEY')

class C:
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

def R(msg):
    return C.red + msg + C.end

def G(msg):
    return C.green + msg + C.end
            
def B(msg):
    return C.blue + msg + C.end
            
def mergedicts(dict1, dict2):
    for k in dict2.keys():
        if type(dict2[k]) is list:
            # dict1[k] is most likely list
            if k in dict1:
                dict1[k].extend(dict2[k])
            else:
                dict1[k] = dict2[k]

class DoError(RuntimeError):
    pass


def callCheck(command, env=None, stdin=None):
    print("about to run\n%s" % command)
    if subprocess.call(command.split(), env=env, stdin=stdin):
        raise Exception("%s failed." % command)


def print_debug():
    import http.client
    """ this will print HTTP requests sent """
    # http://stackoverflow.com/questions/20658572/
    # python-requests-print-entire-http-request-raw
    global DEBUG
    DEBUG = True
    old_send = http.client.HTTPConnection.send
    def new_send( self, data ):
        print("REQUEST:")
        print(urllib.parse.unquote(data.decode()))
        return old_send(self, data)
    http.client.HTTPConnection.send = new_send


class MyAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(MyAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help)

    # this gets called when -d/--debug is passed
    def __call__(self, parser, namespace, values, option_string=None):
        print_debug()
        pass


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

    def __init__(self, api_key):
        self.api_endpoint = API_ENDPOINT
        self.api_key = api_key

    def all_active_droplets(self):
        json_out = self.request('/droplets/')
        return json_out['droplets']

    def get_key_id(self, key_name):
        return get_id_by_attr(key_name, self.all_ssh_keys())

    def get_droplet_id_or_name(self, id_or_name):
        if not id_or_name.isdigit():
            tmp = get_id_by_attr(id_or_name, self.all_active_droplets())
            id = tmp
        else:
            id = id_or_name
        return id

    @argh.aliases('c','create')
    def create_droplet(self, name, ssh_keys=[DO_KEYPAIR_ID],
            image='coreos-stable', region='ams2', size='512mb',
            private_networking=False, backups_enabled=False,
            user_data=None, ipv6=None):
        "Creates droplet. see help for defualts"
        ud = None
        if user_data:
            with open(user_data, 'r') as f:
                ud = f.read()
        params = {
            'name': name,
            'size': size,
            'image': image,
            'region': region,
            'private_networking': private_networking,
            'user_data': ud,
            'ipv6': ipv6,
            'backups': backups_enabled,
        }
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        params['ssh_keys'] = ssh_keys
        json_out = self.request('/droplets', params=params, method='POST')
        return json_out['droplet']

    def show_droplet(self, id):
        
        json_out = self.request('/droplets/%s' % 
                self.get_droplet_id_or_name(id))
        return json_out['droplet']

    @argh.aliases('show')
    def show_droplet_readable(self, id):
        pprint.pprint(self.show_droplet(id))

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

    @argh.aliases('d','destroy')
    def destroy_droplet(self, id, force=False):
        _id = self.get_droplet_id_or_name(id)
        answer = "y"
        if not force:
            answer = input("Do you really want to remove the droplet[y/n]: ")
        if answer == "y":
            json_out = self.request('/droplets/%s' % _id, method='DELETE')
            json_out.pop('status', None)
            return json_out

#regions==========================================
    def all_regions(self):
        json_out = self.request('/regions/')
        return json_out['regions']

#images==========================================
    def all_images(self, distribution='global'):
        params = {'filter': f}
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
    def request(self, path, params={}, method='GET', fetch_all=False):
        if not path.startswith('/'):
            path = '/'+path
        url = self.api_endpoint+path
        headers = { 'Authorization': "Bearer %s" % self.api_key }
        headers['Content-Type'] = 'application/json'

        resp = {}

        while True:
            tmp = self.request_v2(url, params=params, headers=headers,
                                   method=method)
            has_next = 'pages' in tmp['links']
            if has_next:
                has_next = 'next' in tmp['links']['pages']

            if fetch_all and has_next:
                u = urllib.parse.urlparse(tmp['links']['pages']['next'])
                next_page = urllib.parse.parse_qs(u.query)['page'][0]
                params['page'] = next_page
                del(tmp['links'])
                del(tmp['meta'])
                #resp.update(tmp)
                mergedicts(resp, tmp)
            else:
                mergedicts(resp, tmp)
                break

        return resp


    def request_v2(self, url, headers={}, params={}, method='GET'):
        try:
            if method == 'POST':
                resp = requests.post(url, data=json.dumps(params), headers=headers, timeout=60)
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
            print("RESPONSE:")
            print(resp.status_code)
            print(json.dumps(json_out, sort_keys=True, indent=4))

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

    @argh.aliases('s')
    def ssh(self, fuzzy_name, user='core', key=DO_KEY, port='22'):
        chosen = [d for d in self.all_active_droplets()
                  if fuzzy_name in d['name']]
        if len(chosen) > 2 :
            raise DoError("name too ambiguous")   
        if len(chosen) == 0 :
            raise DoError("no droplet by that name")
        ip = self.get_public_ip(chosen[0])
        cmd = "ssh -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s -p %s %s@%s" % (DO_KEY, port, user, ip)
        callCheck(cmd)
                
    def get_private_ip(self, d):
        for n in d['networks']['v4']:
           if n['type'] == 'private':
                return n['ip_address']

    def get_public_ip(self, d):
        for n in d['networks']['v4']:
           if n['type'] == 'public':
                return n['ip_address']

    def status(self, s):
        if s == "new":
            return G(s)
        if s == "active":
            return B(s)
        if s in ["off","archive"]:
            return R(s)
                
    def droplets(self):
        for d in self.all_active_droplets():
            form = "%s[%s] %s -  %s, %s"

            fields = (B(d['name']), G(d['region']['slug']),
                      self.status(d['status']), self.get_public_ip(d), 
                      self.get_private_ip(d))
            print(form % fields)

    def avail(self, s):
        if s:
             return G("available")
        else:
             return R("not avail")

    @argh.aliases('r')
    def regions(self):
        for r in self.all_regions():
            form = "%s: %s, features: %s"

            fields = (B(r['slug']),
                      self.avail(r['available']), ",".join(r['features']))
            print(form % fields)

    @argh.aliases('i')
    @argh.arg('--type', '-t', choices=['application', 'distribution'])
    @argh.arg('--private', '-p', default=False, action='store_true')
    def images(self, type='', private=False, fetch_all=False):
        params = {}
        if type:
            params = {'type': type}
        if private: 
            params = {'private': 'true'}
        for i in self.request('/images/', params=params, fetch_all=fetch_all)['images']:
            form = "%s at %s"
            name = i['slug']
            if not name:
                name = i['name']
            print(form % (R(name), B(",".join( i['regions'] ) )))

    @argh.aliases('k')
    def keypairs(self):
        for k in self.all_ssh_keys():
            form = "%s: id %s, \'%s\'"
            fields = (R(k['name']), B(str(k['id'])), k['public_key'])
            print(form % fields)


class Proxy(object):
    _manager = None
    def __new__(cls, *args, **kwargs):
        if not cls._manager:
            api_token = DO_API_TOKEN
            cls._manager = DoManager(api_token)
        return cls._manager


#def init():
#    """ checks if credentials are present and initalizes the module """
#    manager = Proxy()
#
#    current_module = __import__(__name__)
#
#    for name, method in inspect.getmembers(manager, inspect.ismethod):
#        if name != "__init__":
#            setattr(current_module, name, method)


if __name__ == "__main__":
    do = DoManager(DO_API_TOKEN)

    parser = argh.ArghParser()

    exposed = [do.create_droplet, do.ssh, do.droplets, do.regions, do.keypairs,
               do.destroy_droplet, do.show_droplet_readable, do.images]
    argh.assembling.set_default_command(parser, do.droplets)

    parser.add_commands(exposed)
    parser.add_argument('-d', '--debug', const=False, action=MyAction)


    parser.dispatch()
