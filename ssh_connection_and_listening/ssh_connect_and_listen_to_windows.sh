#!/usr/bin/expect -f
ip=$1
password=$2
spawn ssh -t root@${ip} "stty raw -echo; (stty size; cat) | nc -lvnp 87 -s ${ip}"
expect "assword:"
send "${password}\r"
interact
