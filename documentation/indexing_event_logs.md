# Harvesting smart contract event logs

This is a detailed explaination of how the smart contract search engine indexes smart contract event logs. This is for information/education purposes. This code is executed automatically as part of the search engine's normal operation. 

# An example smart contract
As you can see the smart contract below called `SimpleStorage2` inherits from `SimpleStorage`. We do this because we need to ensure that the smart contract search engine is able to harvest event logs even in situations where there are multiple nested ABIs. You will also notice that there a combination of indexed and non indexed inputs for each event. You will also notice that some functions emit just one event and other functions emit two or more events. These scenarios cover all bases from a testing perspective.

```
pragma solidity >=0.4.0 <0.6.0;

contract SimpleStorage {
    // Event which tests that the harvester can index event logs per ABI (in a nested ABI situation)
    event EventFour(uint256 indexed sseo8, uint256  sseo9);
    event EventFive(uint256 indexed sseo10);
    uint256 ssData;
    // emit two events in the same transaction to test multiple logs in the transactionReceipt
    function set4(uint256 x) public {
        ssData = x;
        emit EventFour(ssData, ssData - 1);
        emit EventFive(ssData);
    }
}

contract SimpleStorage2 is SimpleStorage{
    // Event where both inputs are indexed hence transactionReceipt data will be 0x 
    event EventOne(uint256 indexed sseo1, uint256 indexed sseo2);
    // Event where one input is indexed and one is not hence both topic data and data will need to be accessed
    event EventTwo(uint256 indexed sseo3, uint256  sseo4);
    // Event whre two inputs are indexed and one is not hence there will be 3 topic data and data which all need to be accessed
    event EventThree(uint256 indexed sseo5, uint256 indexed sseo6, uint256 sseo7);
    // Plain var
    uint256 ssData2;

    // emit one event
    function set(uint256 x) public {
        ssData2 = x;
        emit EventOne(ssData2, ssData2 - 1);
    }
    // emit two events in the same transaction to test multiple logs in the transactionReceipt
    function set2(uint256 x) public {
        ssData2 = x;
        emit EventOne(ssData2, ssData2 - 1);
        emit EventTwo(ssData2, ssData2 - 1);
    }
    // emit three events, this covers off all of the different combinations and tests for multiple log/topic/data etc in the transactionReceipt
    function set3(uint256 x) public {
        ssData2 = x;
        emit EventOne(ssData2, ssData2 - 1);
        emit EventTwo(ssData2, ssData2 - 1);
        emit EventThree(ssData2, ssData2 - 1, ssData2);
    }

}
```

# Actual results
When we deploy the `SimpleStorage2` contract and call each of the public functions `set`, `set2`, `set3` and `set4` we get the following results.

## Set
Call the function by passing in the number `10` as the argument
### EventOne
```
{'txEventKey': '0x8732f795b1d16a09c9ca64e433870a9d669c36f037323f671c1c07c7f6f9171a', 'id': '0xdc8fec5c', 'name': 'EventOne', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0xaed53fa0303464ac5a399da63a8b165e04aa4f103871ed6af7d81d413824f366', 'blockNumber': 6681080, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo1', 'type': 'uint256'}, {'indexed': 'True', 'name': 'sseo2', 'type': 'uint256'}], 'eventLogData': {'sseo1': 10, 'sseo2': 9}}
```
As you can see the event log data correctly contains `{'sseo1': 10, 'sseo2': 9}`

## Set2
Call the function by passing in the number `10` as the argument
### EventOne
```
{'txEventKey': '0xed67e29135371f808d4940489f63e7da1629df6cc40eeb758f35aad1c919b60c', 'id': '0xdc8fec5c', 'name': 'EventOne', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0x7219d89c29cde95ba14c3d20cdd8343b4c143d9e3b5891dce96bc3b5d7bb0877', 'blockNumber': 6681571, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo1', 'type': 'uint256'}, {'indexed': 'True', 'name': 'sseo2', 'type': 'uint256'}], 'eventLogData': {'sseo1': 10, 'sseo2': 9}}
```
As you can see the event log data correctly contains `{'sseo1': 10, 'sseo2': 9}`
### EventTwo
```
{'txEventKey': '0x49789c8e85529c0bac1d1885a9802d462a40655527c39357e0aa1ed0b263bf10', 'id': '0x9021d3b7', 'name': 'EventTwo', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0x7219d89c29cde95ba14c3d20cdd8343b4c143d9e3b5891dce96bc3b5d7bb0877', 'blockNumber': 6681571, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo3', 'type': 'uint256'}, {'indexed': 'False', 'name': 'sseo4', 'type': 'uint256'}], 'eventLogData': {'sseo3': 10, 'sseo4': 9}}
```
As you can see the event log data correctly contains `{'sseo3': 10, 'sseo4': 9}`

## Set3

### EventOne
```
{'txEventKey': '0x8f9fdf6e63bf9898b59c52a3bd98c1b5ef6e69d1dd425096e366de6f33ca60a1', 'id': '0xdc8fec5c', 'name': 'EventOne', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0xaaa90f48b06fa6952e564ddc01b5ccc7200b43d6bdf5e6a6a9e9316166f1645b', 'blockNumber': 6682122, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo1', 'type': 'uint256'}, {'indexed': 'True', 'name': 'sseo2', 'type': 'uint256'}], 'eventLogData': {'sseo1': 10, 'sseo2': 9}}
```
As you can see the event log data correctly contains  {'sseo1': 10, 'sseo2': 9}
### EventTwo
```
{'txEventKey': '0xcecc7ad9aa1372ac6e40fb4a34df0d648565ea5fbdfd5059807a5ae3c0c5f250', 'id': '0x9021d3b7', 'name': 'EventTwo', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0xaaa90f48b06fa6952e564ddc01b5ccc7200b43d6bdf5e6a6a9e9316166f1645b', 'blockNumber': 6682122, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo3', 'type': 'uint256'}, {'indexed': 'False', 'name': 'sseo4', 'type': 'uint256'}], 'eventLogData': {'sseo3': 10, 'sseo4': 9}}
```
As you can see the event log data correctly contains `{'sseo3': 10, 'sseo4': 9}`
### EventThree
```
{'txEventKey': '0x21716a1728279df4f023f85401a7c922ba5166ccbd992fea8b830b4e65a5b5e3', 'id': '0x5415ac1e', 'name': 'EventThree', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0xaaa90f48b06fa6952e564ddc01b5ccc7200b43d6bdf5e6a6a9e9316166f1645b', 'blockNumber': 6682122, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo5', 'type': 'uint256'}, {'indexed': 'True', 'name': 'sseo6', 'type': 'uint256'}, {'indexed': 'False', 'name': 'sseo7', 'type': 'uint256'}], 'eventLogData': {'sseo7': 10, 'sseo5': 10, 'sseo6': 9}}
```
As you can see the event log data correctly contains `{'sseo7': 10, 'sseo5': 10, 'sseo6': 9}`

## Set4

### EventFour
```
{'txEventKey': '0x36ce7844bc1bd1779b9749ad72d1cc876ee85cd9918177eb1868d6aaf62a5f2e', 'id': '0xf70a3406', 'name': 'EventFour', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0x9c272f36f80f5678e67f5816a7b85d8283de5457932f6b6ee9ff1da56134dcb3', 'blockNumber': 6682356, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo8', 'type': 'uint256'}, {'indexed': 'False', 'name': 'sseo9', 'type': 'uint256'}], 'eventLogData': {'sseo9': 9, 'sseo8': 10}}
```
As you can see the event log data correctly contains `{'sseo9': 9, 'sseo8': 10}`
### EventFive
```
{'txEventKey': '0xc761a1c96aca12eec60751eebc4e7c47feda61b71dd9676484c32942e91d4b0e', 'id': '0x8acd1506', 'name': 'EventFive', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0x9c272f36f80f5678e67f5816a7b85d8283de5457932f6b6ee9ff1da56134dcb3', 'blockNumber': 6682356, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo10', 'type': 'uint256'}], 'eventLogData': {'sseo10': 10}}
```
As you can see the event log data correctly contains `{'sseo10': 10}`

# Code logic
The logic behind the event log harvesting code is as follows.

## Loop through each block
The [code iterates over each block](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L18) (from latest to earilest)

## Loop through each transaction 
If the transaction count in the block in question is greater than 0 then [the code iterates through each transaction](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L22)

## Loop through log events
A transaction can have more than one event log (as we have demonstrated above). [The code iterates through all of the event logs](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L30), processing each one individually.

## Loop through all ABIs
The smart contract search engine facilitates the indexing of contract which have many nested ABIs (a side effect of inheritence). [The code fetches the ABIs which pertain to a given contract address and then processes the event log in question in accordance with that specific ABI](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L34)

## Identify the contract's events and inputs
[The code uses the contract's ABI to identify the events as well as the event's inputs](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L60). The code builds lists for event input type and event input name as well as separate lists for type and name in the event that the inputs are defined as `indexed`. This is important because the data is accessed differently depending on whether the input is indexed or not.

Events which are indexed keep all of their data in the topic section of the transaction receipt. Event inputs which are not indexed keep their data in the transaction receipt's data area.

## Obtaining the actual data
Once we have all of the important information i.e blockNumber, transactioHash as well as the metadata about the event (name, type, indexed etc.) we can go ahead and get the actual data. We do not use web3 for this. Instead we determine the characteristics for each of the events and their inputs and then decode the data manually. You will notice that [the code can differentiate between events where all of the inputs are indexed vs where there is a combination of indexed and non indexed](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L112). These data extraction methods are performed as close to the metal as possible. Whilst this requires extra more complex coding, I find that it is more reliable than using high level libraries and filters etc. There have been cases where I have noticed events missing and have also experienced timeouts when creating filters which are too inclusive (which try and get all logs at once etc.)

## Loading data into the ES index
The final product from this process is an `eventDict` dictionary. [The code builds this dict automatically](https://github.com/second-state/smart-contract-search-engine/blob/master/python/utilities_and_tests/event_log_harvest_testing.py#L125). This is valid JSON and therefore can be uploaded straight into Elasticsearch.

The next step for this code, now that it is all tested, is to integrate this into the single `harvest.py` file.
