#!/usr/bin/expect -f
ip=$1
password=$2
spawn ssh -t root@${ip} "nc -lvnp 87 -s ${ip}"
expect "assword:"
send "${password}\r"
interact
