# (0xm4ud) 2023 - 0xm4ud.github.io 
# 0xm4ud Eth_scrapper

import requests
#import json
from bs4 import BeautifulSoup
from optparse import OptionParser

green ='\x1b[0;32m'
yellow = '\x1b[0;33m'
red ='\x1b[0;31m'
normal = '\x1b[0m'


#target_block = 8660077
# Define the number of transactions to print
#num_txs_to_print = 3
# Initialize a counter for the number of printed transactions
printed_txs = 0

#Current block number, an approximation of the latest block mined in case no block number is specified
# tool will subtract 10000000 blocks from the current block number unless you specify a block number
#use -b or --sBlock to specify a block number
def getRelevantBlock():
    # Func is a little hack to get a initial near the latest relevant block
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    response = requests.get('https://etherscan.io/blocks', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find(lambda tag: tag.name == 'div' and "Showing blocks between" in tag.text)
    block_text = div.text
    currentBlock = block_text.split('#')[1].split(' ')[0]
    return currentBlock

currentBlock = getRelevantBlock()

def get_current_block_number(api_key):
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error: Etherscan API request failed with status code {response.status_code}")
    
    data = response.json()

    if not data['result']:
        raise Exception(f"Error: Failed to get current block number")

    # The block number is returned in hexadecimal format, convert it to decimal
    return int(data['result'], 16)


def get_tx_by_hash(tx_hash, api_key):
    url = f"https://api-goerli.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error: Etherscan API request failed with status code {response.status_code}")

    data = response.json()

    if not data['result']:
        raise Exception(f"Error: No transaction found with hash: {tx_hash}")

    return data['result']

def get_internal_txs_by_address(address, start_block, end_block, api_key):
    url = f"https://api-goerli.etherscan.io/api?module=account&action=txlistinternal&address={address}&startblock={start_block}&endblock={end_block}&sort=asc&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error: Etherscan API request failed with status code {response.status_code}")
    
    data = response.json()
    
    if data['status'] != "1":
        raise Exception(f"Error: Etherscan API request failed with message: {data['message']}")

    return data['result']


def get_normal_txs_by_address(address, start_block, end_block, api_key):
    print("Start Block: ", start_block)
    url = f"https://api-goerli.etherscan.io/api?module=account&action=txlist&address={address}&startblock={start_block}&endblock={end_block}&sort=asc&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error: Etherscan API request failed with status code {response.status_code}")
    
    data = response.json()
    
    if data['status'] != "1":
        raise Exception(f"Error: Etherscan API request failed with message: {data['message']}")

    return data['result']


def get_printed(idx, tx, type):
    if type == "normal":
        print(f"Transaction {idx + 1}:")
        print(f"  Block Number: {tx['blockNumber']}")
        print(f"  TransactionHash: {tx['hash']}")
        print(f"  From: {tx['from']}")
        print(f"  To: {tx['to']}")
        print(f"  SigHash: {tx['methodId']}")
        print(f"  Value: {tx['value']} wei")
        print(f"  Input data: {tx['input']}\n")
    elif type == "internal":
        print(f"Transaction {idx + 1}:")
        print(f"  Block Number: {tx['blockNumber']}")
        print(f"  TransactionHash: {tx['hash']}")
        print(f"  From: {tx['from']}")
        print(f"  To: {tx['to']}")
        print(f"  Value: {tx['value']} wei")
        print(f"  Input data: {tx['input']}\n")      

class TxScrapper:
    def __init__(self, options):
      #TODO define options next to self above!
        self.address = options.address
        self.tx_hash = options.tx_hash
        self.api_key = options.api_key
        self.target_block = options.target_block
        self.num_txs_to_print = options.num_txs_to_print

    def print_normal_txs(self, normal_txs, target_block, num_txs_to_print, printed_txs):
        print(green,"\rStart of Normal Transactions:",normal) # how do I color this? 
        print(green,"\r==================================\r\n",normal)  
        if len(normal_txs) == 0:
            print("No normal transactions found for the specified address and block range.")
        else:
            for idx, tx in enumerate(normal_txs):
                # new blocky 3 lines so far
                block_num = int(tx['blockNumber'])

            # Check if the block number of the current transaction is greater than the target block
                if block_num > int(target_block) and int(tx['value']) > 0: # remove and tx['value'] > 0 if you want to print all transactions
                    # If so, print the transaction
                    print(f"Normal Transaction {printed_txs + 1} after block {target_block} is in block {block_num}:")
                    #print(json.dumps(tx, indent=4))
                    type="normal"
                    get_printed(idx, tx, type)
                    # Increment the counter for the number of printed transactions
                    printed_txs += 1
                    # If we have printed the desired number of transactions, break the loop
                    if printed_txs >= int(num_txs_to_print):
                        break
        print(red,"\rEnd of Normal Transactions",normal) # how do I color this?
        print(red,"\r==================================",normal,"\r\n")

    def print_internal_txs(self, internal_txs, target_block, num_txs_to_print, printed_txs):
        print(green,"\rStart of Internal Transactions:",normal)
        print(green,"\r==================================\r\n",normal)  
        # For internal transactions
        if len(internal_txs) == 0:
            print("No normal transactions found for the specified address and block range.")
        else:
            for idx, tx in enumerate(internal_txs):
                # new blocky 3 lines so far
                block_num = int(tx['blockNumber'])
            # Check if the block number of the current transaction is greater than the target block
                if block_num > int(target_block) and int(tx['value']) > 0: # remove and tx['value'] > 0 if you want to print all transactions
                    # If so, print the transaction
                    print(f"Internal Transaction {printed_txs + 1} after block {target_block} is in block {block_num}:")
                    #print(json.dumps(tx, indent=4))
                    type="internal"
                    get_printed(idx, tx, type)
                    # Increment the counter for the number of printed transactions
                    printed_txs += 1
                    # If we have printed the desired number of transactions, break the loop
                    if printed_txs >= int(num_txs_to_print):
                        break
        print(red,"\rEnd of Internal Transactions",normal) # how do I color this? 
        print(red,"\r==================================",normal,"\r\n")

    def start_scrapping(self):
        api_key = self.api_key
        if len(self.tx_hash) != 0:
            tx_hash = self.tx_hash
            if tx_hash.startswith('0x'):
                tx_hash = tx_hash[2:]
                hash_txs = get_tx_by_hash(tx_hash, api_key)
                print(f"  Block Number: {int(hash_txs['blockNumber'],16)}")
                print(f"  TransactionHash: {hash_txs['hash']}")
                print(f"  From: {hash_txs['from']}")
                print(f"  To: {hash_txs['to']}")
                print(f"  Value: {int(hash_txs['value'],16)} wei")
                print(f"  Input data: {hash_txs['input']}\n")
                exit()
            else:
                hash_txs = get_tx_by_hash(tx_hash, api_key)
                print(f"  Block Number: {int(hash_txs['blockNumber'],16)}")
                print(f"  TransactionHash: {hash_txs['hash']}")
                print(f"  From: {hash_txs['from']}")
                print(f"  To: {hash_txs['to']}")
                print(f"  Value: {int(hash_txs['value'],16)} wei")
                print(f"  Input data: {hash_txs['input']}\n")
                exit()
        else:
            normal_txs = get_normal_txs_by_address(self.address, start_block=self.target_block, end_block='latest', api_key=api_key)
            internal_txs = get_internal_txs_by_address(self.address, start_block=self.target_block, end_block='latest', api_key=api_key)  

            self.print_normal_txs(normal_txs, self.target_block, self.num_txs_to_print, printed_txs)
            self.print_internal_txs(internal_txs, self.target_block, self.num_txs_to_print, printed_txs)

def main():
    currentBlock = getRelevantBlock()
    parser = OptionParser()
    msg = "Target address"
    parser.add_option("-a", "--address", dest="address", help="[ Required ] Target address")
    msg = "API to be used"
    parser.add_option("-x", "--api", dest="api_key", help="[ Required ] API key")
    parser.add_option("-t", "--txhash", dest="tx_hash", default="" , help="Target TX hash")
    parser.add_option("-n", "--numTxs", dest="num_txs_to_print", default=3, help="Number of transactions to print")
    parser.add_option("-b", "--sBlock", dest="target_block", default=(int(currentBlock)-10000000) ,help="Target start block number")

    (options, args) = parser.parse_args()

    if not options.api_key:
        parser.error('API key not given')
        exit()
    
    if not options.tx_hash:
        if not options.address:
            parser.error('Address nor TX hash given given')
            exit()
        else:
            if options.api_key and options.address:
                TxScrapper(options).start_scrapping()
    else:
        if options.api_key and options.tx_hash:
            TxScrapper(options).start_scrapping()

if __name__ == "__main__":
    main()
