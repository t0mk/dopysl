# Digital Ocean PYthon wrapper that Sucks Less

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy

## Installation

clone this and

```
cp dopysl.py ~/bin/dopysl
```

I don't care for pip and/or setuptools.

## Getting Started

Credentials for DigitalOcean API should be passed in environment variables. Only APIv2 is supported.

You need to find out the api token from https://cloud.digitalocean.com/settings/applications and you shoud set it as envvar:

```sh
export DO_API_TOKEN=...
```

## Usage

You have to call the dopysl.init() first to authenticate.

To list all the droplets:

```python
import dopysl
dopysl.init()
print dopysl.all_active_droplets()
```

alternatively more prettily:

```python
import dopysl
import json

pp = lambda chunk: json.dumps(chunk, sort_keys=True, indent=4)

dopysl.init()
pp(dopysl.all_active_droplets())
```

If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

```python
dopysl.init()
dopysl.new_droplet('new_vm', '512mb', 'lamp', 'ams2')
```

If you use APIv1 you first need to get ID of those.

# Methods

The methods are self explanatory. 

```
dopysl.init()
dopysl.show_domain('exapmle.com')
dopysl.new_droplet('new_droplet', '512mb', 'lamp', 'ams2')
```

More in https://github.com/t0mk/dopysl/blob/master/dopysl.py
