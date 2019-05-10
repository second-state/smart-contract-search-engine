import os
import configparser


class Harvest:
    def __init__(self):
        self.scriptExecutionLocation = os.getcwd()
        print("Reading configuration file")
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read('config.ini')

        # ABI[s]
        self.abis = {}
        for key in config['smartContractAbis']:
            stringKey = str(key)
            self.urls[stringKey] = config['smartContractAbis'][key]
        print("\nABIs:")
        for (ufaKey, ufaValue) in self.urls.items():
            print(ufaKey + ": " + ufaValue)

# Driver - Start
harvester = Harvest()

