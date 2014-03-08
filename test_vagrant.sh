#!/bin/bash
set -e
vagrant destroy -f
vagrant up
curl -sL -w "%{http_code}\\n" http://192.168.111.222/data -o /dev/null | grep -q "200"
vagrant provision
curl -sL -w "%{http_code}\\n" http://192.168.111.222/data -o /dev/null | grep -q "200"
