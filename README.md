# Digital Ocean PYthon wrapper that Sucks Less

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy

## Installation

```
pip install dopysl
```

## Getting Started

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

.. code-block:: bash

    # export DO_CLIENT_ID='client_id'
    # export DO_API_KEY='long_api_key'

.. code-block:: pycon

    >>> from dopy.manager import DoManager
    >>> do = DoManager('client_id', 'long_api_key')

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
