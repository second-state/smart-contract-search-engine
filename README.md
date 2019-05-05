# Smart Contract Search Engine

This search engine is designed to run locally (from your file system without the need for a server).

This search engine can also be hosted publicly by simply copying this entire project into the htdocs folder of a LAMP server, as seen here < http://54.66.215.89/index.html >.

## Searching - Frontend

This system is running live at the following endpoint < http://54.66.215.89/index.html >. Please feel free to try it out, using the following examples of usage.

### Example usage

#### Search using address

You can search the system using the address of product-giveaway contract owners, product-giveaway players, product-giveaway winners and even product-giveaway smart contract addresses.

![Demonstration address](images/demonstration_address.png)

#### Search using plain text 

You can also search the system using plain text; for example try typing the word "demonstration" into the search box as shown below.

![Demonstration image](images/demonstration_text.png)

#### Search using both address and plain text

You can also search the system using plain text, with the addition of an address. The following example shows how the "demonstration" text (which produced 3 results above) is now filtered to a single contract address of `0x7e38f41F7562720D1F219D474C78d98152382BFe`. You can try this out for yourself, just paste in the address and text.

#### Show/Hide Details

To make the results cleaner, we have provided the clickable "Show / Hide Details" text. This will reveal or hide additional information such as the list of winners, block number of when the contract was last interacted with and so forth.

![Demonstration image](images/demonstration_show.png)


## Harvesting - Backend

The harvesting scripts are written in Python; they require a particular smart contract's ABI file and a link to the blockchain's RPC endpoint.

### Full - smart contract harvest

The Python file, at `python/SmartContractHarvesterFull.py` harvests the entire blockchain (in reverse, from the latest block, right back to the genesis block).

```python3
for blockNumber in reversed(range(latestBlockNumber)):
```

The full - smart contract harvest, technically, only needs to be run once. However, if you like you can set it to run once per day using a cron job such as the following. 

```bash
# m h  dom mon dow   command
45 22 * * * cd ~/htdocs/python && /usr/bin/python3 SmartContractHarvesterFull.py
# The above cron job will trigger at 10:45pm every day
# Please note that you can obtain your system's time using the "date" command
# Please note that the python path, for your unique system, can be obtained via the "which python3" command
```

Keep in mind, the full - smart contract harvest does check if each contract instance already exists (and so there is no real downside to running it daily or weekly). Think of this harvest as a full sweep of the entire blockchain.

You can check to see if the `SmartContractHarvesterFull.py` script is running via the following command.

```bash
ps ax | grep SmartContractHarvesterFull.py
```
**Note:** You can supress the output from the cron job by adding the following to the end of the line. This prevents the /var/mail of your OS from growing too large.
```
>/dev/null 2>&1
```

### Topup - smart contract harvest

The Python file, at `python/SmartContractHarvesterTopup.py` must be run regularly. This script, when run regularly, will index brand new smart contracts by scanning the most recent 350 blocks. 

```python3
stop = latestBlockNumber - 350
for blockNumber in reversed(range(stop, latestBlockNumber)):
```

The topup - smart contract harvest, can be run once per minute using the following cron job. Again, remember that this script will only index contract instances which do not already exist in the index. If a contract instance already exists this script will just skip over it and continue looking for new unindexed contract instances. This is a very cheap and efficient script; essentially just sweeps a finite amount of upper blocks in the chain over and over as time goes on.

```bash
* * * * * cd ~/htdocs/python && /usr/bin/python3 SmartContractHarvesterTopup.py
# The above cron job will trigger at every minute of every hour of every day
```

### Incremental  - smart contract **STATE** update

The above scripts primarily store the contract infrastructure (contract address, owner address etc.). Having the ABI and contract address means that we can create web3 instances of each contract instance; and then go ahead and read all of the contract's public variables. The above harvesting scripts do this **only once**.

The Python file, at `python/FairPlayStateUpdate.py` checks for changes in each contract's state in real-time. As soon as any change is detected, the main index is updated. The Python script does not repeatedly query the main index. Instead it locally compares hashes (hash(smart contract address + smart contract state)). This is very efficient and fast.

### Configuring your own search engine system

Using the publicly available frontend is easy and free. However, if you would like to run your own infrastructure, please following the instructions below. These examples are all for the latest Ubuntu LTS.

#### Operating system libraries

Python3

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3
```
Pip3

```bash
sudo apt-get install python3-pip
pip3 install --upgrade pip
```

Boto3
```bash
pip3 install boto3
```
#### Elasticsearch



#### Amazon Web Services (AWS)

Authentication


