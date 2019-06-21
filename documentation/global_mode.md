# Global mode

## Apache 2
The following instructions will facilitate a fresh Apache 2 and Virtual Host installation on Ubuntu 18.04LTS

Update system and install Apache2
```bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install apache2
```

List the firewall rules and add Apache2 on port 80 only
```
sudo ufw app list
sudo ufw allow 'Apache'
```
Please also make sure that any overarching AWS ports are open (if this server is being hosted inside an AWS account).

Check that Apache is running
```
sudo systemctl status apache2
```
Enable modules for the proxy 
```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
```

Get the domain name (as discussed at the start of this page) and use it in the following steps
i.e. search-engine.com or 13.236.179.58 (just the IP without the protocol). In this example, we are just using fictitious search-engine.com 

Set up Virtual Host
```
sudo mkdir -p /var/www/search-engine.com/html
sudo chown -R $USER:$USER /var/www/search-engine.com/html
sudo chmod -R 755 /var/www/search-engine.com
```

Create the following configuration file
```
sudo vi /etc/apache2/sites-available/search-engine.com.conf
```
Add the following content to the file which you just created (note: we will explain the Proxy component a little later in this document). Obviously you will need to replace search-engine.com with your public IP/Domain
```
<VirtualHost *:80>
    ProxyPreserveHost On
    ProxyPass /api http://127.0.0.1:8080/api
    ProxyPassReverse /api http://127.0.0.1:8080/api
    ServerAdmin admin@search-engine.com
    ServerName search-engine.com
    ServerAlias www.search-engine.com
    DocumentRoot /var/www/search-engine.com/html
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
Enable the new site
```
sudo a2ensite search-engine.com.conf
```

Disable the original Apache2 site
```
sudo a2dissite 000-default.conf
```

Test the configuration which we just created
```
sudo apache2ctl configtest
```

Reload the system to show the new site
```
sudo systemctl reload apache2
```

Here is a quick reference of commands which you will find usefull in the future
```
## Stop and start
sudo systemctl stop apache2
sudo systemctl start apache2
## Restart
sudo systemctl restart apache2
## Reload without interuption
sudo systemctl reload apache2
```

## Search engine source code
```bash
cd ~
git clone https://github.com/second-state/smart-contract-search-engine.git
```

Place the code in the appropriate directories
```bash
cp -rp ~/smart-contract-search-engine/* /var/www/search-engine.com/html/
```
Set final permissions on all files
```bash
sudo chown -R $USER:$USER /var/www/search-engine.com/*
```

## Global mode config

Go to the appropriate directory (where the search engine will be served by Apache2) i.e. `cd /var/www/search-engine.com/html/`. We will be staying in that area for all of the following work.

### Javascript
This system uses a single Javascript file which passes events and data back and forth between the HTML and Python. The code repository currently has one Javascript file `secondStateJS.js` which services the [FairPlay - Product Giveaway site](https://cmt.search.secondstate.io/) and one Javascript file `ethJS.js` which services the [Ethereum Search Engine Demonstration](https://ethereum.search.secondstate.io/). One of the strong points of this search engine is that it allows you to create your own custom HTML/JS so that you can render your data in any way.

**publicIp**
If running this in global mode, please make sure that the `var publicIp = "";` in the [secondStateJS.js file](../js/secondStateJS.js) is set to the public domain name of the server which is hosting the search engine (including the protocol) i.e. 
```
var publicIp = "https://www.search-engine.com"; //No trailing slash please
```

**searchEngineNetwork in secondStateJS.js**
Please ensure that the correct network id is set in the "searchEngineNetwork" variable in the secondStateJS.js file i.e.
```
var searchEngineNetwork = "18"; // CyberMiles MainNet
```

**esIndexName name in secondStateJS.js**
Please ensure that the appropriate index name will be set (depending on which network you selected in the previous step)
The logic is as follows.
```
if (searchEngineNetwork == "19") {
    blockExplorer = "https://testnet.cmttracking.io/";
    esIndexName = "testnet";
}

if (searchEngineNetwork == "18") {
    blockExplorer = "https://www.cmttracking.io/";
    esIndexName = "cmtmainnetmultiabi";
}
```
Just please make sure that you set the esIndexName to the same value as the config.ini (i.e. note how the below config.ini common index and the above secondStateJS.js esIndexName are both set to testnet).

**This Javascript configuration will be made part of the global configuration as per the GitHub Issue**
```
[commonindex]
network = testnet
```

```
if (searchEngineNetwork == "19") {
    blockExplorer = "https://testnet.cmttracking.io/";
    esIndexName = "testnet";
}

if (searchEngineNetwork == "18") {
    blockExplorer = "https://www.cmttracking.io/";
    esIndexName = "cmtmainnetmultiabi";
}
```


**Blockchain -> rpc variable in config.ini**
It is important that the search engine is pointing to the correct RPC endpoint i.e. CMT TestNet vs MainNet
```
[blockchain]
rpc = https://testnet-rpc.cybermiles.io:8545
```

**Elasticsearch**
Please also put in your Elasticsearch URL and region.

```
[blockchain]
rpc = https://testnet-rpc.cybermiles.io:8545

[elasticSearch]
endpoint = search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com
aws_region = ap-southeast-2

```

**Index names**
The masterindex, abiindex and bytecode index can all stay as they are below. You might just want to change the commonindex to be more descriptive i.e. mainnet, testnet etc.

```
[masterindex]
all = all

[abiindex]
abi = abi

[bytecodeindex]
bytecode = bytecode

[commonindex]
network = cmttestnetmultiabi
```

## SSL (HTTPS) using "lets encrypt"
```
sudo wget https://dl.eff.org/certbot-auto -O /usr/sbin/certbot-auto
```
```
sudo chmod a+x /usr/sbin/certbot-auto
```
```
sudo certbot-auto --apache -d search-engine.com  -d www.search-engine.com
```

## Python
**Please perform the steps in this [subsection of the harvesting documentation](https://github.com/second-state/smart-contract-search-engine/blob/master/documentation/harvesting.md#preparing-your-operating-system-for-harvesting---installing-the-necessary-libraries) to ensure that your system can run the Python code. Once that is done, you can continue with installing Flask (as shown directly below)**

## Flask
```
python3.6 -m pip install Flask --user
```

## Python Flask / Apache2 Integration

```bash
sudo ufw allow ssh
sudo ufw enable
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp
```

Open crontab for editing
```bash
crontab -e
```
Add the following line inside crontab
```bash
@reboot sudo ufw enable
@reboot cd ~/smart-contract-search-engine/python && nohup /usr/bin/python3.6 io.py >/dev/null 2>&1 &
```

## CORS (Allowing Javascript, from anywhere, to access the API)

Whilst the API can be accessed from anywhere using REST clients like Postman etc. DApps and websites will also want to access the data in the search engine API by visiting the domain (where the search engine is being hosted) via port 80 i.e.

```
_data = {"query":{"multi_match":{"fields":["functionData.title","functionData.desc"],"query":"Win"}}}
var _dataString = JSON.stringify(_data);
```

```
response1 = $.ajax({
    url: "https://search-engine.com/api/es_search",
    type: "POST",
    data: _dataString,
    dataType: "json",
    contentType: "application/json",
    success: function(response) {
        console.log(response);
    },
    error: function(xhr) {
        console.log("Get items failed");
    }
});
```
Without CORS enabled (on Apache) the above Javascript query will cause the following error.

```
Access to XMLHttpRequest at 'https://search-engine.com/api/es_search' from origin 'https://theDapp.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```
To enable CORS please following these instructions.

Ensure that Apache2 has the mod_rewrite enabled

```
sudo a2enmod rewrite
```

Ensure that Apache2 has the headers library enabled by typing the following command.

```
sudo a2enmod headers
```

Open the `/etc/apache2/apache2.conf` file and add the following.
```
<Directory /var/www/search-engine>
     Order Allow,Deny
     Allow from all
     AllowOverride all
     Header set Access-Control-Allow-Origin "*"
</Directory>
```

Then in addition to this, please open the `/etc/apache2/sites-enabled/search-engine-le-ssl.conf` file (which was created automatically by the above "lets encrypt" command) and add the following code inside the <VirtualHost *:443> section.

```
Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "POST, GET, OPTIONS"
Header always set Access-Control-Max-Age "1000"
Header always set Access-Control-Allow-Headers "x-requested-with, Content-Type, origin, authorization, accept, client-security-token"
RewriteEngine On
RewriteCond %{REQUEST_METHOD} OPTIONS
RewriteRule ^(.*)$ $1 [R=200,L]
```

Restart the server and then test again using the above Javascript code.

## Activate the harvesting
Please make sure that you have followed [the harvesting documentation](https://github.com/second-state/smart-contract-search-engine/blob/master/documentation/harvesting.md) which shows you how to set up the automatic cron tasks for the harvesting/indexing scripts.

Also once all of this is done, please just give the server a quick reboot; during this time all of the processes will fire off as per the cron etc.
```
sudo shutdown -r now
```
