# Digital Ocean PYthon wrapper that Sucks Less

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy

## Installation

```
pip install dopysl
```

## Getting Started

Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.
If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

dopy.Proxy().new_droplet('new_vm', '512mb', 'lamp', 'ams2')

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


To interact with Digital Ocean, you first need .. a digital ocean account with
valid API keys.

Keys can be set either as Env variables, or within the code.

For API v.2.

```
export DO_API_TOKEN='api_token'
```

```
from dopy.manager import DoManager
do = DoManager(None, 'api_token', api_version=2)
```


For API v.1.

```
export DO_CLIENT_ID='client_id'
export DO_API_KEY='long_api_key'
```

```
from dopy.manager import DoManager
do = DoManager('client_id', 'long_api_key')
```


# Methods

The methods of the DoManager are self explanatory; ex.

```
do.all_active_droplets()
do.show_droplet('12345')
do.destroy_droplet('12345')
do.all_regions()
do.all_images()
do.all_ssh_keys()
do.sizes()
do.all_domains()
do.new_droplet('new_droplet', 66, 1601, 1)
```

The methods for v.2 API are similar, the only difference
is using names instead of IDs for domains and slugs for
sizes, images and datacenters; ex.

```
do.show_domain('exapmle.com')
do.new_droplet('new_droplet', '512mb', 'lamp', 'ams2')
```


https://github.com/t0mk/dopysl
