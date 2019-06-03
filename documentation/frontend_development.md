

## How to display blockchain data in a custom format

### Contract version

Each contract instance has an ABI and Bytecode. If is possible however for the following to occur.
- a single ABI can be shared by many contract instances with the same Bytecode (identical contracts deployed at different addresses)
- a single ABI dan be shared by many contract instances with different Bytecode (i.e. ERC721 where each new contract instance has a different statically typed token acronym in its source code)

We need to have a way in which we can uniquely identify contract instances. We do this in the following way.

We hash the ABI using sha3 and we store this as a value (called `abiSha3`) in the index (along side the other information like contract address etc.)


```
"_source": {
...
"abiSha3": "0x6718b332159313dce48c26e0e51c512040a3de930017555a03ba540c5b80235c",
...
```

We also hash the Bytecode and we store this as a value (called `bytecodeSha3`) in the index (along side the other information like contract address etc.)

```
"_source": 
...
"bytecodeSha3": "0x672ab6f7bef2b8f8c34b0dd7d37bef9fcbf0567899ed182278aeee91bb4b7bd5",
...
```

The above hashes enable anyone who knows the ABI and Bytecode, to search for them in the backend. This provides great flexibillity.

We then go a step further and combine the two values `abiSha3` and `bytecodeSha3` and the create a sha3 hash of them. This provides us with a third (the most unique and useful identifier in terms of contract instance version) value called `abiSha3BytecodeSha3`

It makes sense to store these hashes because this is a really robust way to deterministically understand the data. The frontend (a search results page or DApp) just needs to convert this data to whatever format it needs it in. For example, the following Javascript displays version 1 ("v1") or version 2 ("v2") depending on the unique ABI/Bytecode combination which is their unique smart contract instance.


```
// Setting Dapp Version
if (value._source.abiSha3BytecodeSha3 == "0x0afaf8e4843da5ea7a78bb01088fde7ad5bcfabc1cffc9851adb9fa41389d44e"){
        dappVersion = "v1";
    }
    else if (value._source.abiSha3BytecodeSha3 == "0xa1c025708a54ed04595d075658a563e454ac4595eff966113b81447dce3c4340") {
        dappVersion = "v2";
    }
```

### Contract date information

The harvester calls every available function (including the public getters and setters which the compiler creates for public variables) and stores the data in the index under the "functionData" section. Any additional display rules such as date formatting need to be performed in the secondStateJS.js file. Take this example for displaying an epoch value (which the smart contract is hard-wired to do) in the frontend, using Javascript.

```
if (epochRepresentation.toString().length == 10) {
    var endDate = new Date(epochRepresentation * 1000);
} else if (epochRepresentation.toString().length == 13) {
    var endDate = new Date(epochRepresentation);
```

The above code takes a value like `1559290380` and converts it to a more understandable value like `Fri May 31 2019 18:13:00 GMT+10`.

### Justification

Manipulating the data between the blockchain and the backend index will cause unruly headaches and increase maintenance to a point which is unsustainable. It is best to store the data verbatim and then allow the frontend applications to convert that to any representation required. To take this point further a game may want to display a different frontend image depending on whether a value is 0 or 1 or 2. It makes more sense to leave that up to the frontend developer than to try parse the data between the blockchain and the index (to create substitutions and then store the image paths in the index; this makes the index unusable for someone else with a different frontend design)