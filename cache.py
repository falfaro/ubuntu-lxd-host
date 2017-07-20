#!/usr/bin/env python

import datetime
import os
import time

from pylxd import Client


def _container_ipv4_addresses(container, interfaces=['eth0'], ignore_devices=['lo']):
    network = container.state().network
    network = dict((k, v) for k, v in network.items() if k in interfaces and k not in ignore_devices) or {}
    addresses = dict((k, [a['address'] for a in v['addresses'] if a['family'] == 'inet']) for k, v in network.items()) or {}
    return addresses


def _has_all_ipv4_addresses(addresses):
    return len(addresses) > 0 and all([len(v) > 0 for v in addresses.itervalues()])


def _get_addresses(container, timeout=30):
    due = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < due:
        time.sleep(1)
        addresses = _container_ipv4_addresses(container)
        if _has_all_ipv4_addresses(addresses):
            return addresses


def create_container(client, config):
    if not client.containers.exists('cache'):
        container = client.containers.create(config, wait=True)
        container.start(wait=True)
        # Waits for the container to have network connectivity
        print 'Waiting for network in the container...'
        _get_addresses(container)
    else:
        container = client.containers.get('cache')

    return container


def apt_update(container, dist_upgrade=False):
    if not apt_update.initialized:
        print container.execute(['/usr/bin/apt-get', 'update']).stdout
        if dist_upgrade:
            print container.execute(['/usr/bin/apt-get', '-y', 'dist-upgrade']).stdout
    apt_update.initialized = True
apt_update.initialized = False


def apt_install(container, *packages):
    environment = {
        'DEBIAN_FRONTEND': 'noninteractive',
        }
    cmd = ['/usr/bin/apt-get', '-y', 'install']
    cmd += packages
    print container.execute(cmd, environment=environment).stdout


def main():
    # This override is required because of conjure-up built-in LXC/LXD
    # part of the Snap package, which does not cope well with Ubuntu's
    # own LXC/LXD shipped as a .deb packages.
    os.environ['LXD_DIR'] = '/var/snap/conjure-up/common/lxd'
    client = Client()

    container = create_container(client=client, config = {
        'name': 'cache',
        'profiles': ['nested'],
        'source': {
            "type": "image",
            "protocol": "simplestreams",
            "server": "https://cloud-images.ubuntu.com/daily",
            "alias": "17.04"
            }
        })

    apt_update(container, dist_upgrade=True)
    apt_install(container, 'apache2', 'apt-cacher')
    apt_install(container, 'etckeeper')
    with open('apt-cacher.conf', 'r') as f:
        container.files.put('/etc/apt-cacher/apt-cacher.conf', f.read())
    print container.execute(['/bin/systemctl', 'restart', 'apt-cacher']).stdout


if __name__ == "__main__":
    # execute only if run as a script
    main()
