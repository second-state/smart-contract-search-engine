# Smart Contract Search Engine

## Local vs Global

This search engine is designed to run in two modalities:
- local, single end-user mode (without the need for a server). See [local-mode documentation](./documentation/local_mode.md)
- global, multiple end-user mode (where the search engine is made available to the world via a server). See [global-mode documentation](documentation/global_mode.md)

## Frontend Demonstration

We have put together a "live" [demonstration of the search engine running in global mode](http://54.66.215.89/index.html). At this early stage, we have indexed this particular [Product Giveaway Smart Contract](https://github.com/CyberMiles/smart_contracts/blob/master/FairPlay/FairPlay.lity). 

Below are some basic usage examples. Please see the [documentation](./documentation) section for details on how to deploy your own Smart Contract Search Engine.

---

### Pre defined queries

You can click any of the 3 pre defined queries. The results are based on the address in your browsers wallet ([i.e. CyberMiles Venus Chrome Extension](https://www.cybermiles.io/en-us/blockchain-infrastructure/venus/))

![Demonstration address](documentation/images/predefined_queries.gif)

---

### Search using plain text 

You can also search the system using plain text; for example try typing the words "Cup Cake" into the search box as shown below.

![Demonstration address](documentation/images/advanced_search.gif)

---

### Search using address

You can search the system using the **address** of:
- a contract
- an owner 
- a player
- a winner 

![Demonstration address](documentation/images/advanced_search2.gif)

---
