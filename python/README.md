Please put all of your settings (index names, blockchain RPC etc) into the config.in file

The harvest.py file can be run as follows

```
#!/bin/bash
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m full >/dev/null 2>&1 &
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m topup >/dev/null 2>&1 &
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m state >/dev/null 2>&1 &
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m tx >/dev/null 2>&1 &
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m abi >/dev/null 2>&1 &
cd ~/smart-contract-search-engine/python && nohup python3.7 harvest.py -m indexed >/dev/null 2>&1 &
```

There is no need for cron etc. because each of these modes is self managing.

Once called (as shown above) each mode repeats indefinitely.

Each of the modes has a designated completion time. If code executes before this time is up it will sleep for the remainder of time.

This product utilize Python multithreading to greatly improve any inevitable I/O bottlenecks.

The [more detailed documentation of this entire product](https://github.com/second-state/smart-contract-search-engine/tree/master/documentation) is under heavy development. Please feel free to ask questions.
