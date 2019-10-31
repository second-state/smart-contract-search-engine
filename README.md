# Smart Contract Search Engine

## Local vs Global

This search engine is designed to run in two modalities:
- local, single end-user mode (without the need for a server). See [local-mode documentation](./documentation/local_mode.md)
- global, multiple end-user mode (where the search engine is made available to the world via a server). See [global-mode documentation](https://docs.secondstate.io/smart-contracts-search-engine/start-a-search-engine)

## Frontend Demonstration

We have put together a: 
- live TestNet [demonstration of the search engine running on the CyberMiles TestNet](https://testnet.cmt.search.secondstate.io)
- live MainNet [demonstration of the search engine running on the CyberMiles MainNet](https://cmt.search.secondstate.io)

Specifically, we have indexed this particular [Product Giveaway Smart Contract](https://github.com/CyberMiles/smart_contracts/blob/master/FairPlay/FairPlay.lity) from both the aforementioned networks (TestNet and MainNet).

---

### General search

You can search for smart contracts on the blockchain without even installing a wallet or Chrome extension. Simply click "Search" to get all results, or type in contract addresses and text to filter the results.
![Search](documentation/images/search.gif)

---

### Personalized search using predefined queries

If you want to take it a step further, you can download the [CyberMiles Chrome Extension](https://www.cybermiles.io/en-us/blockchain-infrastructure/venus/) and intimately search the block chain in the context of your very own accounts. Here is a quick demonstration.

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
