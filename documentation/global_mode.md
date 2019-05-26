# Global mode

If running this in global mode, please make sure that the `var publicIp = "";` in the [secondStateJS.js file](../js/secondStateJS.js) is set to the public domain name OR public IP address of the server which is hosting the search engine (including the protocol) i.e. http://search-engine.com OR http://123.45.6.7

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

Check that Apache is running
```
sudo systemctl status apache2
```

Get the public IP address or domain name (as discussed at the start of this page) and use it in the following steps
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

## Python
Please perform the steps in this [subsection of the harvesting documentation](https://github.com/second-state/smart-contract-search-engine/blob/master/documentation/harvesting.md#preparing-your-system-for-harvesting) to ensure that your system can run the Python code. Once that is done, you can continue with installing Flask (as shown directly below)

## Flask
```
python3.6 -m pip install Flask --user
```

Search engine source code
```bash
cd ~
git clone https://github.com/second-state/smart-contract-search-engine.git
```

Place the code in the appropriate directories
```bash
sudo cp -rp ~/smart-contract-search-engine/* /var/www/search-engine.com/
sudo mv /var/www/search-engine.com/*.html /var/www/search-engine.com/html/
```
Set final permissions on all files
```bash
sudo chown -R $USER:$USER /var/www/search-engine.com/*
```

## Python Flask / Apache2 Integration

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
```

```bash
cd ~
FLASK_APP=/var/www/search-engine.com/python/io.py flask run --port=8080 >/dev/null 2>&1 &
```


```bash
sudo ufw allow ssh
sudo ufw enable
sudo ufw allow 8080/tcp
```

Open crontab for editing
```bash
crontab -e
```
Add the following line inside crontab
```bash
@reboot sudo ufw enable
```
