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
You can chance keyfile and keypair id in command parameters. The aforementioned variables are just for defaults.


## Usage

```
$ dopysl
$ dopysl k
$ dopysl r
$ dopysl ssh fuzzy_name
$ dopysl help
$ dopysl help create
$ dopysl create help
```

The last command creates small coreos-stable droplet with name "help" :).
