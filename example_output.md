Examples of blocks with no transactions
```bash
tpmccallum$ python3 FairPlayHarvester.py 

Latest block is 1563541

Processing block number 1563540
Skipping block number 1563540 - No transactions found!

Processing block number 1563539
Skipping block number 1563539 - No transactions found!
```

Example of block with transactions of value which are not smart contract related

```bash
Processing block number 1563538
Transaction count: 1.
Processing transaction hex: 0x1d86997e9d66899f20bca2fcfed8760f87c89ad0c5e1b5d9c7ca260fee2e8501 
This transaction does not involve a contract, so we will ignore it
```

Example of a block which has the FairPlay smart contract deployed in it

```bash
Processing block number 1563537
Transaction count: 1.
Processing transaction hex: 0x104fd86cb49ab11944c742f95a219b2edecb05af915355dd4ffecd6085886e22 
Found contract address: 0x07B664DbD2315fe0c0bffD17Cc66220B7401cb60 
Found a match: 053ba7d0 
Found a match: 0eecae21 
Found a match: 1b9c5c35 
Found a match: 200d2ed2 
Found a match: 370158ea 
Found a match: 408eace6 
Found a match: 4a79d50c 
Found a match: 4b114691 
Found a match: 55f150f1 
Found a match: 824f4baf 
Found a match: 87a8e30e 
Found a match: 8da5cb5b 
Found a match: c7ab74a4 
All hashes match!
Contract address: 0x07B664DbD2315fe0c0bffD17Cc66220B7401cb60 
```
Back to processing blocks in reverse order

```bash
Processing block number 1563536
Skipping block number 1563536 - No transactions found!

Processing block number 1563535
Skipping block number 1563535 - No transactions found!

Processing block number 1563534
Skipping block number 1563534 - No transactions found!
```
