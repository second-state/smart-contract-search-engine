# Harvesting smart contract event logs

This is a detailed explaination of how the smart contract search engine indexes smart contract event logs. This is for information/education purposes. This code is executed automatically as part of the search engine's normal operation. 

# An example smart contract
As you can see the smart contract below called `SimpleStorage2` inherits from `SimpleStorage`. We do this because we need to ensure that the smart contract search engine is able to harvest event logs even in situations where there are multiple nested ABIs.

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
```
{'txEventKey': '0x8732f795b1d16a09c9ca64e433870a9d669c36f037323f671c1c07c7f6f9171a', 'id': '0xdc8fec5c', 'name': 'EventOne', 'contractAddress': '0x982785C0983522079eD58FDfd92d56DdA43613ed', 'TxHash': '0xaed53fa0303464ac5a399da63a8b165e04aa4f103871ed6af7d81d413824f366', 'blockNumber': 6681080, 'from': '0xd7617c5e4f0aaeb288e622764cf0d34fa5acefe8', 'inputs': [{'indexed': 'True', 'name': 'sseo1', 'type': 'uint256'}, {'indexed': 'True', 'name': 'sseo2', 'type': 'uint256'}], 'eventLogData': {'sseo1': 10, 'sseo2': 9}}
```
As you can see the event log data correctly contains `{'sseo1': 10, 'sseo2': 9}`
