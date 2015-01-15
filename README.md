# Digital Ocean PYthon wrapper that Sucks Less

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy

## Installation

```
pip install dopysl
```

## Getting Started

Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.

If you want to use APIv2, you need to find out the api token from https://cloud.digitalocean.com/settings/applications and you shoud set it as envvar:

```sh
export DO_API_TOKEN=...
```

If you still want to use APIv1 you need to define client ID and API key. **!!!Beware, API key for v1 is different than API token for v2 !!!**. Find it out from https://cloud.digitalocean.com/api_access and set it as:

```sh
export DO_CLIENT_ID=...
export DO_API_KEY=...
```

## Usage

Theres is as Proxy singleton which you can use to query DigitalOcean API. To list all the droplets:

```python
import dopysl
print dopysl.Proxy.all_active_droplets()
```

alternatively more prettily:

```python
import dopysl
import json

pp = lambda chunk: json.dumps(chunk, sort_keys=True, indent=4)

pp(dopysl.Proxy.all_active_droplets())
```

If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

```python
dopysl.Proxy().new_droplet('new_vm', '512mb', 'lamp', 'ams2')
```

If you use APIv1 you first need to get ID of those.

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

More in https://github.com/t0mk/dopysl/blob/master/dopy/manager.py
