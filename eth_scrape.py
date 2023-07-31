import requests
import json
from brownie.utils import color

green ='\x1b[0;32m'
yellow = color("yellow")
red =color("red")
normal = color("none")

api_key='API_HERE'
address='ADDRESS_HERE'
# Define the transaction hash when you find a transaction that you want to inspect
# else the tx_hash should be empty ex: tx_hash = ""
tx_hash = ""
#tx_hash = ""
#defines block target (if you don't to get every transaction since genesis block)
target_block = 8660077
# Define the number of transactions to print
num_txs_to_print = 3
# Initialize a counter for the number of printed transactions
printed_txs = 0


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
    url = f"https://api-goerli.etherscan.io/api?module=account&action=txlist&address={address}&startblock={start_block}&endblock={end_block}&sort=asc&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error: Etherscan API request failed with status code {response.status_code}")
    
    data = response.json()
    
    if data['status'] != "1":
        raise Exception(f"Error: Etherscan API request failed with message: {data['message']}")
 
    return data['result']

# Check if the tx_hash is not empty if not empty then print the transaction
if len(tx_hash) != 0:
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


normal_txs = get_normal_txs_by_address(address, start_block=8660077, end_block='latest', api_key=api_key)
internal_txs = get_internal_txs_by_address(address, start_block=8660077, end_block='latest', api_key=api_key)

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


def print_normal_txs(normal_txs, target_block, num_txs_to_print, printed_txs):
    print(green,"\rStart of Normal Transactions:",normal) # how do I color this? 
    print(green,"\r==================================\r\n",normal)  
    if len(normal_txs) == 0:
        print("No normal transactions found for the specified address and block range.")
    else:
        for idx, tx in enumerate(normal_txs):

            # new blocky 3 lines so far
            block_num = int(tx['blockNumber'])
        # Check if the block number of the current transaction is greater than the target block
            if block_num > target_block and int(tx['value']) > 0: # remove and tx['value'] > 0 if you want to print all transactions
                # If so, print the transaction
                print(f"Normal Transaction {printed_txs + 1} after block {target_block} is in block {block_num}:")
                #print(json.dumps(tx, indent=4))
                type="normal"
                get_printed(idx, tx, type)
                # Increment the counter for the number of printed transactions
                printed_txs += 1

                # If we have printed the desired number of transactions, break the loop
                if printed_txs >= num_txs_to_print:
                    break
    print(red,"\rEnd of Normal Transactions",normal) # how do I color this?
    print(red,"\r==================================",normal,"\r\n")

def print_internal_txs(internal_txs, target_block, num_txs_to_print, printed_txs):
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
            if block_num > target_block and int(tx['value']) > 0: # remove and tx['value'] > 0 if you want to print all transactions
                # If so, print the transaction
                print(f"Internal Transaction {printed_txs + 1} after block {target_block} is in block {block_num}:")
                #print(json.dumps(tx, indent=4))
                type="internal"
                get_printed(idx, tx, type)
                # Increment the counter for the number of printed transactions
                printed_txs += 1

                # If we have printed the desired number of transactions, break the loop
                if printed_txs >= num_txs_to_print:
                    break
    print(red,"\rEnd of Internal Transactions",normal) # how do I color this? 
    print(red,"\r==================================",normal,"\r\n")

print_normal_txs(normal_txs, target_block, num_txs_to_print, printed_txs)
print_internal_txs(internal_txs, target_block, num_txs_to_print, printed_txs)
