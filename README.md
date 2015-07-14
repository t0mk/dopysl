# Digital Ocean PYthon wrapper that Sucks Less using APIv2

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy. I use only APIv2.

## Installation

```
sudo apt-get install python3-pip
sudo python3.4 -m pip install argh
```

then clone this to your ~bin/

```
cd bin
git clone https://github.com/t0mk/dopysl.git
```

I don't care for pip and/or setuptools.

## Setup

in your .bashrc/.zshrc set

```

PATH=${PATH}:~/bin/dopysl

# this is the v2 API token from 
# https://cloud.digitalocean.com/settings/tokens/new
export DO_API_TOKEN=

# find out your favorite keypair id from "$ dopysl keypairs" (after you set and
# export the DO_API_TOKEN)
export DO_KEYPAIR_ID=

# the file with private key from your favorite keypair.
export DO_KEY=
```
You can chance keyfile and keypair id in parameters. The aforementioned variables are just for defaults.


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
