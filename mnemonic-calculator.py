# mnemonic phrase address creator
# made by manmallard
# https://github.com/manmallard/mnemonic-calculator

import hdwallet
import random
import os
import time
import multiprocessing
import sys
from mnemonic import Mnemonic
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator
import binascii

DATABASE = r'database test/11_13_2022/'

def int_to_hex(num, num_bytes):
    """Convert an integer to its hexadecimal representation."""
    return hex(num)[2:].zfill(num_bytes * 2)

def generate_random_mnemonic(num_words=24, language='english'):
    """Generate a random mnemonic phrase."""
    mnemo = Mnemonic(language.upper())
    strength = int(2 ** (num_words / 3))
    mnemonic_words = mnemo.generate(256)
    return mnemonic_words

def generate_primary_key_and_address(wordcount=24, coin='BTC', verbose=0, language='english'):
    """Generate primary key and address."""
    mnemonic_phrase = generate_random_mnemonic(wordcount, language)
##    mnemonic = Bip39MnemonicGenerator(mnemonic_phrase, language)
    seed_bytes = Bip39SeedGenerator(mnemonic_phrase).Generate()
    seed_hex = binascii.hexlify(seed_bytes).decode('utf-8')
    wallet = hdwallet.HDWallet(symbol='BTC').from_seed(seed=seed_hex)
    #coin_type_key = wallet.generate_coin_type(coin)
    #primary_key = wallet.primary_key()
    private_key = wallet.private_key()
    public_key = wallet.public_key()
    address = wallet.p2pkh_address()
    if verbose:
        print(address)
    return mnemonic_phrase, private_key, public_key, address
def timer():
    """Measure the time it takes to generate a primary key and address."""
    start = time.time()
    generate_primary_key_and_address()
    end = time.time()
    print("Time taken:", end - start)

def main(database, args):
    """Main function for generating addresses."""
    while True:
        # Generate private key and address
        passphrase, _, _, address = generate_primary_key_and_address(args['wordcount'], args['coin'], args['verbose'], args['language'])
        with multiprocessing.Lock():
            with open('addresses.txt', 'a') as file:
                file.write(passphrase + ', ' + address + '\n')
        if args['verbose']:
            print(address)
        if address[-args['substring']:] in database:
            print('Potential match:', address)
            for filename in os.listdir(DATABASE):
                with open(DATABASE + filename) as file:
                    if address in file.read():
                        print('Match!\n')
                        with open('plutus.txt', 'a') as plutus:
                            plutus.write('hex private key: ' + str(private_key_hex) + '\n' +
                                         'public key: ' + str(public_key_hex) + '\n' +
                                         'uncompressed address: ' + str(address) + '\n\n')
                        break
                    else:
                        print('No match\n')

def print_help():
    """Print help information."""
    print('''Plutus homepage: https://github.com/manmallard/mnemonic-calculator
mnemonic-calculator QA support: https://github.com/manmallard/mnemonic-calculator/issues

Speed test: 
execute 'python3 menmonic-calculator.py time', the output will be the time it takes to bruteforce a single address in seconds

Quick start: run command 'python3 menmonic-calculator.py'

By default this program runs with parameters:
python3 menmonic-calculator.py verbose=0 substring=8

verbose: must be 0 or 1. If 1, then every bitcoin address that gets bruteforced will be printed to the terminal. This has the potential to slow the program down. An input of 0 will not print anything to the terminal and the bruteforcing will work silently. By default verbose is 0.

substring: to make the program memory efficient, the entire bitcoin address is not loaded from the database. Only the last <substring> characters are loaded. This significantly reduces the amount of RAM required to run the program. if you still get memory errors then try making this number smaller, by default it is set to 8. This opens us up to getting false positives (empty addresses mistaken as funded) with a probability of 1/(16^<substring>), however it does NOT leave us vulnerable to false negatives (funded addresses being mistaken as empty) so this is an acceptable compromise.

cpu_count: number of cores to run concurrently. More cores = more resource usage but faster bruteforcing. Omit this parameter to run with the maximum number of cores

triedvalues: list of tried passphrases, default triedpassphrases.json in plutuspassphrase folder

language: language to pick words from, default is random, and will choose a random language every time it generates a passphrase, possible languages are: "chinese_simplified", "spanish", "portuguese", "korean", "italian", "japanese", "french", "english", "czech", "chinese_traditional"

wordcount: specify mnemonic word count, default 24

coin: default BTC ''')

if __name__ == '__main__':
    args = {
        'verbose': 0,
        'substring': 8,
        'cpu_count': multiprocessing.cpu_count(),
        'triedvalues': 'triedpassphrases.txt',
        'language': 'english',
        'wordcount': 24,
        'coin': 'BTC'
    }

    for arg in sys.argv[1:]:
        command, value = arg.split('=')
        if command == 'help':
            print_help()
        elif command == 'time':
            timer()
        elif command == 'cpu_count':
            cpu_count = int(value)
            if 0 < cpu_count <= multiprocessing.cpu_count():
                args['cpu_count'] = cpu_count
            else:
                print('Invalid input. cpu_count must be greater than 0 and less than or equal to', multiprocessing.cpu_count())
                sys.exit(-1)
        elif command == 'verbose':
            verbose = int(value)
            if verbose in [0, 1]:
                args['verbose'] = verbose
            else:
                print('Invalid input. verbose must be 0 (false) or 1 (true)')
                sys.exit(-1)
        elif command == 'substring':
            substring = int(value)
            if 0 < substring < 27:
                args['substring'] = substring
            else:
                print('Invalid input. substring must be greater than 0 and less than 27')
                sys.exit(-1)
        elif command == 'triedvalues':
            args['triedvalues'] = value
        elif command == 'language':
            args['language'] = value.lower()  # Convert language to lowercase
        elif command == 'wordcount':
            args['wordcount'] = int(value)
        elif command == 'coin':
            args['coin'] = value
        else:
            print('Invalid input:', command)
            print_help()
            sys.exit(-1)


    
    print('reading database files...')
    database = set()
    for filename in os.listdir(DATABASE):
        with open(DATABASE + filename) as file:
            for address in file:
                address = address.strip()
                if address.startswith('1'):
                    database.add(address[-args['substring']:])
    print('DONE')

    print('database size: ' + str(len(database)))
    print('processes spawned: ' + str(args['cpu_count']))

    
    for cpu in range(args['cpu_count']):
        multiprocessing.Process(target = main, args = (database, args)).start()
