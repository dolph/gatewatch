#!/bin/bash
set -e
vagrant destroy -f
time vagrant up
curl -sL -w "%{http_code}\\n" http://192.168.111.222/data -o /dev/null | grep -q "200"
time vagrant provision
curl -sL -w "%{http_code}\\n" http://192.168.111.222/data -o /dev/null | grep -q "200"
