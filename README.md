# Smart Contract Search Engine

This search engine is designed to run locally (from your file system without the need for a server).

This search engine can also be hosted publicly by simply copying this entire project into the htdocs folder of a LAMP server.

The harvester is written in Python; it requires a smart contract's ABI file and a link to the blockchain's RPC endpoint.

At present (in its MVP form) this system uses an Elasticsearch instance which is restricted to a few IP addresses. If you would like to use this system, please raise an issue and we can organize to have your IP address listed. You could also spin up your own Elasticsearch instance locally and run the Python file.

## Public Access

This system is also running live at the following endpoint < http://54.66.215.89/index.html >. At this stage you will be able to access the Product Giveaway DApp information on the CyberMiles Testnet.

### Example usage

#### Search using address

You can search the system using the address of product-giveaway contract owners, product-giveaway players, product-giveaway winners and even product-giveaway smart contract addresses.

![Demonstration image](images/demonstration_text.png)

You can also search the system using plain text; for example try typing the word "demonstration" into the search box as shown below.

![]()



