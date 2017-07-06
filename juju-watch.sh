#!/bin/sh
watch -c lxc exec $1 -- sudo -u ubuntu -i juju status --color
