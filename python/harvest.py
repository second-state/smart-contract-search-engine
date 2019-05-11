import os
import configparser


class Harvest:
    def __init__(self):
        self.scriptExecutionLocation = os.getcwd()
        print("Reading configuration file")
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(os.path.join(self.scriptExecutionLocation, 'config.ini'))
        # ABI[s]
        self.abis = {}
        for key in config['abis']:
            stringKey = str(key)
            self.abis[stringKey] = config['abis'][key]
        print("\nABIs:")
        for (ufaKey, ufaValue) in self.abis.items():
            print(ufaKey + ": " + ufaValue)
        self.blockchainRpc = config['blockchain']['rpc']
        print("Blockchain RPC: %s" % self.blockchainRpc)
        self.elasticSearchIndex = config['elasticSearch']['index']
        print("ElasticSearch Index: %s" % self.elasticSearchIndex)
        self.elasticSearchEndpoint = config['elasticSearch']['endpoint']
        print("ElasticSearch Endpoint: %s" % self.elasticSearchEndpoint)


# Driver - Start
harvester = Harvest()

