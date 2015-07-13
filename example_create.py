#!/usr/bin/env python

import dopysl

KEY_NAME = 'tkarasek_key'

def create(_key_id):
    dopysl.new_droplet(
        name='dev',
        size='512mb',
        region='ams2',
        image='coreos-stable',
        ssh_keys=_key_id,
     )

dopysl.print_debug()
dopysl.init()

create(dopysl.get_key_id(KEY_NAME))



