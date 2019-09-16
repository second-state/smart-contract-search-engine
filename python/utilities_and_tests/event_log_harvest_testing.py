import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

event_filter = harvester.web3.eth.filter('latest')
for event in event_filter.get_new_entries():
	print(event)