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

![Demonstration address](images/demonstration_address.png)

#### Search using plain text 

You can also search the system using plain text; for example try typing the word "demonstration" into the search box as shown below.

![Demonstration image](images/demonstration_text.png)

#### Search using both address and plain text

You can also search the system using plain text, with the addition of an address. The following example shows how the "demonstration" text (which produced 3 results above) is now filtered to a single contract address of `0x7e38f41F7562720D1F219D474C78d98152382BFe`. You can try this out for yourself, just paste in the address and text.

#### Show/Hide Details

To make the results cleaner, we have provided the clickable "Show / Hide Details" text. This will reveal or hide additional information such as the list of winners, block number of when the contract was last interacted with and so forth.

![Demonstration image](images/demonstration_show.png)


