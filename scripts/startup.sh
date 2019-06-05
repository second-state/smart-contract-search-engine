#!/bin/bash

while true
do
  STATUS=$(curl --max-time 30 -s -o /dev/null -w '%{http_code}' https://testnet-rpc.cybermiles.io:8545)
  if [ $STATUS -eq 200 ]; then
    nohup /usr/bin/python3.6 harvest.py -m full >/dev/null 2>&1 &
    nohup /usr/bin/python3.6 harvest.py -m topup >/dev/null 2>&1 &
    nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &
    nohup /usr/bin/python3.6 harvest.py -m bytecode >/dev/null 2>&1 &
    nohup /usr/bin/python3.6 harvest_all.py -m full >/dev/null 2>&1 &
    nohup /usr/bin/python3.6 harvest_all.py -m topup >/dev/null 2>&1 &
    break
  else
    echo "Got $STATUS please wait"
  fi
  sleep 10
done
