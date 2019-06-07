# Using docker

The following instructions help you to build docker image with [global_mode](https://github.com/second-state/smart-contract-search-engine/blob/master/documentation/global_mode.md)

1. Get source code

```
git clone https://github.com/second-state/smart-contract-search-engine.git
cd smart-contract-search-engine
```

2. Edit configurations files
    - ServerName in apache config `config/site.conf`
    - rpc, elasticsearch configs in `python/config.ini`
    - IP in `js/secondStateJS.js`

```
vim config/site.conf
vim python/config.ini
vim js/secondStateJS.js
```

3. Configure `awscli`

```
aws configure
```

3. Build docker image

```
docker build -f docker/Dockerfile -t search-engine .
```

4. Start docker container
    - After starting container, supervisord will run startup.sh once and handle apache2 & flask services.

```
docker run -it --rm -p 8080:80 -v $HOME/.aws:/root/.aws search-engine
```

Now you can visit `http://<your_host>:8080` to check your smart contract search engine.

# Accessing the Docker command line

Once the Docker instance is running you can get the ID of the container using the following command.
```
docker ps -q
```

Once you have this ID you can open a bash terminal inside the Docker container environment.

```
docker exec -it PasteTheID bash
```
