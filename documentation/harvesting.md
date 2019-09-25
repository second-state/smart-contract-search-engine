## Harvesting 
Please follow the instructions below so that your system can automatically execute all of the search engine's scripts.

# Preparing your operating system for harvesting - installing the necessary libraries

The harvesting/indexing requires a few software libraries (to enable Python to talk to blockchain RPC, Elasticsearch as well as fetch data from URLs etc.). Please follow these instructions to ensure that your system can successfully run the Python scripts.

## Operating system libraries

Python3

```bash
sudo apt-get -y update
sudo apt-get -y upgrade

# If using Ubuntu 18.04LTS Python 3.6 will already be installed

# If using older Ubuntu, you will need to install Python3.6 and Python3.6-dev 
#sudo add-apt-repository ppa:jonathonf/python-3.6
#sudo apt-get -y update
#sudo apt-get install python3.6-dev 
```
Pip3

```bash
sudo apt-get -y install python3-pip
```

Eth-Abi
```
python3.6 -m pip install eth-abi --user
```

Web3

```
python3.6 -m pip install web3 --user
```

Boto3

```bash
python3.6 -m pip install boto3 --user
```
AWS Requests Auth
```
python3.6 -m pip install aws_requests_auth --user
```

AWS Command Line Interface (CLI)

```
sudo apt-get install awscli
```

Configuring AWS CLI

```
aws configure
```
**AWS Access Key ID:** The aws configure script will request that you add your "AWS Access Key ID". Your AWS Access Key ID can be found by clicking on "users" and then the "security credentials" tab at your [console home](https://console.aws.amazon.com/iam/home); as shown below. If you are creating a new AWS Access Key ID, remember to store the Secret Access Key (as it is only ever displayed here this once) ... you will need the Secret Access Key in the next step.

![Demonstration image](images/access_key_id.png)

**AWS Secret Access Key:** This is obtained when you create the AWS Access Key ID (as per the previous step).

**Default region name:** There is a table of regions, you can see the region in the top right corner of your EC2 console. Use the following table to convert this to the appropriate name i.e. Sydney = "ap-southeast-2".

![Demonstration image](images/region_table.png)

**Default output format:** The default output format can stay as None; just hit enter.

Elasticsearch

```
python3.6 -m pip install elasticsearch --user
```

## Elasticsearch

**AWS provides Elasticsearch as a service. To set up an AWS Elasticsearch instance visit your AWS console using the following URL.**
```
https://console.aws.amazon.com/console/home
```
**Type "Elasticsearch" into the Find Services section of the AWS console.**

![Demonstration image](images/find_services.png)

**Click the "Create a new domain" button.**

![Demonstration image](images/create_new_es_domain.png)

Choose the appropriate machine[s] for your cluster, keeping in mind [the pricing of each machine](https://aws.amazon.com/ec2/pricing/on-demand/). Remember that you can also set up [cost, usage and reservation budgets](https://console.aws.amazon.com/billing/home?region=us-east-1#/budgets/create?type=COST) as well as [cost alerts and cost forecasts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) to avoid surprises. Please also remember that Elasticsearch instances (domains and indexes) are region specific. Make sure that you remember which region you used to initialize the instance (you will also need this region information later for authentication and access control).

## Amazon Web Services (AWS)

**Authentication and access control**

All of the blockchain data is public so there is no real need to restric access. However, we want to ensure that this global access is **Read-Only** and that write access is restricted to the appropriate IP/Domain/User etc.

Please read the [Amazon Elasticsearch Service Access Control](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-ac.html) documentation. This very flexible authentication and access control can be set up after the fact by writing a policy.

To modify the policy, for a specific index, click on the "Modify access policy" button.

![Demonstration image](images/modify_access.png)

**Restrict everyone, but allow your AWS user to perform any task**
We have just set up `aws configure` on our search engine server, so now its file system has the ability to communicate with the Elasticsearch index. It does so on behalf of a particular end user who's entry point into our system is that end user's web browser. In the global set up we use a combination of Python flask, Apache2 and a ReverseProxy. It is all very easy to set up, as documented in the [global_mode.md](https://github.com/second-state/smart-contract-search-engine/blob/master/documentation/global_mode.md)
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::007383469891:user/tpmccallum"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:ap-southeast-2:007383469891:domain/smart-contract-search-engine/*"
    }
  ]
}
```

**Note:** The `Action` for the `Principal` (with the IAM user) is `es:*` (wildcard) and in contrast the `Action` for the `Principal` (open to the public) is restructed to only HTTP Get (`es:ESHttpGet`)


The arn:aws:iam above can be found in [your AWS IAM console](https://console.aws.amazon.com/iam/home#/home)

![Demonstration image](images/iam.png)


# ABI and Bytecode

At present the system reads ABIs and Bytecode from the abi and bytecode indexes respectively. At present these are both populted by static code which is below. There will be a user interface for users to upload both ABIs and bytecode in the very near future.

Please use this code for now. It will upload the FairPlay V1 and FairPlay V2 ABI and Bytecode. The user interface will eventually allow anyone to upload ABIs and Bytecode and then the search engine will go ahead and harvest them automatically.

```
https://github.com/second-state/smart-contract-search-engine/blob/master/python/load_v1_v2_abi_byecode.py
```


### Recommended usage - Run once at startup!
**Run at startup**

Technically speaking you will just want to run all of these commands the **one** time, at startup!. 
The system will take care of itself. Here is an example of how to run this once at startup.

**Step 1**
Create a bash file, say, `~/startup.sh` and make it executable with the `chmod a+x` command. Then put the following code in the file. 
**Please**  be sure to replace `https://testnet-rpc.cybermiles.io:8545` with that of your RPC.

```bash
#!/bin/bash
while true
do
  STATUS=$(curl --max-time 30 -s -o /dev/null -w '%{http_code}' https://YOUR RPC NODE GOES HERE)
  if [ $STATUS -eq 200 ]; then
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m init >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m abi >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m full >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m topup >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m tx >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m state >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m bytecode >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m indexed >/dev/null 2>&1 &
    cd /var/www/search-engine.com/html/python && ulimit -n 10000 && nohup /usr/bin/python3.6 harvest.py -m faster_state >/dev/null 2>&1 &
    break
  else
    echo "Got $STATUS please wait"
  fi
  sleep 10
done
```
**Step 2**
Add the following command to cron using `crontab -e` command.
```bash
@reboot ~/startup.sh
```
The smart contract search engine will autonomously harvest upon bootup.

## Keep alive
The following script ensures that the system will wait out any time periods where the RPC endpoint is not available. The system will essentially perform a quick reboot if the RPC goes down. You may have already noticed that the startup1.sh and startup2.sh scripts perform a similar URL status check; so rest assured that they will not start harvesting again until the RPC endpoint is back up.

Please create the following bash script and make it executable using `chmod`. Please be sure to use your own RPC endpoint as apposed to the `https://testnet-rpc.cybermiles.io:8545` here.
```
#!/bin/bash
STATUS=$(curl --max-time 30 -s -o /dev/null -w '%{http_code}' https://testnet-rpc.cybermiles.io:8545)
if [ $STATUS -eq 200 ]; then
  echo "Got 200! All done!"
else
  HARVEST_COUNT=$(ps ax | grep harvest.py | wc -l)
  if [ $HARVEST_COUNT -le 2 ]; then 
    echo "Obviously the system just rebooted so we are still waiting for the startup1.sh & startup2.sh scripts to activate (this will only happen when the RPC endpoint is back in service)"
  else
    echo "It seems that we have harvesting processes running but no working RPC endpoint, time to reboot... "
    sudo shutdown -r now
  fi 
fi
```

Please add the following to your crontab -e
```
* * * * * nohup ~/rpcCheck.sh >/dev/null 2>&1 &
```

# Known system errors

## Error 1
ModuleNotFoundError: No module named 'apt_pkg'

## Fix 1
```
sudo apt-get remove python3-apt
sudo apt-get install python3-apt
```

## Error 2
RequestsDependencyWarning: urllib3 (1.25.2) or chardet (3.0.4) doesn't match a supported version!

## Fix 2
```
python3.6 -m pip uninstall chardet
python3.6 -m pip uninstall urllib3
python3.6 -m pip install urllib3 --user
python3.6 -m pip install chardet --user
python3.6 -m pip uninstall requests
python3.6 -m pip install requests --user
```

## Error 3
Elasticsearch only allows 1000 unique field types. For example in a single index you should only ever need less than 1000 fields such as "name", "address" etc. However, we are all contract data and so the field count could exceeded this limit.
```
elasticsearch.exceptions.RequestError: RequestError(400, 'illegal_argument_exception', '[fXAH4Nb][x.x.x.x:9300][indices:data/write/update[s]]')
```
## Fix 3
You can raise the limit of fields using the following simple PUT request.
https://discuss.elastic.co/t/total-fields-limit-setting/53004

# Alternative operating systems
In some cases you may want to run just a single component of this harvester on different hardware (MacOS instead of Ubuntu). The following is a quick reference example of how the core Elasticsearch, AWS and Web3 libraries can be installed on MacOS under a Virtual Environment.
```
# Install virtual env
sudo pip install virtualenv
virtualenv -p python3 ~/.venv-py3
# Or don't specify the python
# virtualenv ~/.venv-py3
# Activate the virtual env
source ~/.venv-py3/bin/activate
# Set up the search engine environment to run the Python scripts
pip install --upgrade pip setuptools
pip install --upgrade web3
pip install --upgrade boto3
pip install --upgrade aws_requests_auth
pip install --upgrade awscli
pip install --upgrade elasticsearch
aws configure
```


