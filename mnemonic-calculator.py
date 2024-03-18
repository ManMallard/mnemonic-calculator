# mnemonic phrase address creator
# made by manmallard
# https://github.com/manmallard/mnemonic-calculator

import hdwallet
import random
import os
import time
import multiprocessing
import select
import sys
import platform

DATABASE = r'database/11_13_2022/'

def generate_random_mnemonic(num_words=24, language='english'):
    """Generate a random mnemonic phrase."""
    if language not in BIP39.LANGUAGES:
        raise ValueError("Invalid language. Supported languages are: " + ', '.join(BIP39.LANGUAGES))
    
    word_list = BIP39.get_word_list(language)
    mnemonic_words = random.choices(word_list, k=num_words)
    return ' '.join(mnemonic_words)

def generate_primary_key_and_address(wordcount=24, coin='BTC', verbose='0', language='english'):
    """Generate primary key and address."""
    mnemonic_phrase = generate_random_mnemonic(wordcount)
    seed_bytes = BIP39.mnemonic_to_seed(mnemonic_phrase)
    wallet = HDWallet.from_seed(seed_bytes)
    coin_type_key = wallet.generate_coin_type(coin)
    primary_key = coin_type_key.key
    private_key_hex = int_to_hex(primary_key.secret, 32)
    public_key_hex = primary_key.public_key().to_hex(compressed=True)
    address = primary_key.address()
    if verbose:
        print(address)
    return mnemonic_phrase, private_key_hex, public_key_hex, address

def timer(args, lock):
    start = time.time()
    passphrase, private_key, public_key, address = generate_primary_key_and_address(args['wordcount'], args['coin'],args['verbose'], args['language'])
    end = time.time()
    print(str(end-start))
    sys.exit(0)
    
def main(database, args):
    """Main function for generating addresses."""
    lock = multiprocessing.Lock()
    while True:
        # Check for 'q' input
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            input_str = sys.stdin.readline().strip()
            if input_str == 'q':
                break
        # Generate private key and address
        passphrase, private_key, public_key, address = generate_primary_key_and_address(args['wordcount'], args['coin'],args['verbose'], args['language'])
        lock.acquire()
        with open('addresses.txt', 'ab') as file:
            file.write(passphrase.encode('utf-8') + b', ' + address.encode('utf-8') + b'\n')
        lock.release()
        if args['verbose']:
            print(address)
        if address[-args['substring']:] in database:
            print('potential match: ' + address)
            lock.acquire()
            for filename in os.listdir(DATABASE):
                with open(DATABASE + filename) as file:
                    if address in file.read():
                        print('match! \n')
                        with open('plutus.txt', 'a') as plutus:
                            plutus.write('hex private key: ' + str(private_key) + '\n' +
                                         'WIF private key: ' + str(private_key_to_wif(private_key)) + '\n'
                                         'public key: ' + str(public_key) + '\n' +
                                         'uncompressed address: ' + str(address) + '\n\n')
                        break
                    else:
                        print('no match \n')
            lock.release()

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

    
    sys.exit(0)

if __name__ == '__main__':
    args = {
        'verbose': 0,
        'substring': 8,
        'cpu_count': multiprocessing.cpu_count(),
        'triedvalues': 'triedpassphrases.txt',
        'language': 'random',
        'wordcount': 24,
        'coin': 'BTC'
    }
    lock = multiprocessing.Lock()
    
    for arg in sys.argv[1:]:
        command, value = arg.split('=')
        if command == 'help':
            print_help()
        elif command == 'time':
            timer(args, lock)
        elif command == 'cpu_count':
            cpu_count = int(value)
            if 0 < cpu_count <= multiprocessing.cpu_count():
                args['cpu_count'] = cpu_count
            else:
                print('invalid input. cpu_count must be greater than 0 and less than or equal to ' + str(multiprocessing.cpu_count()))
                sys.exit(-1)
        elif command == 'verbose':
            verbose = int(value)
            if verbose in [0, 1]:
                args['verbose'] = verbose
            else:
                print('invalid input. verbose must be 0(false) or 1(true)')
                sys.exit(-1)
        elif command == 'substring':
            substring = int(value)
            if 0 < substring < 27:
                args['substring'] = substring
            else:
                print('invalid input. substring must be greater than 0 and less than 27')
                sys.exit(-1)
        elif command == 'triedvalues':
            args['triedvalues'] = value
        elif command == 'language':
            args['language'] = value
        elif command == 'wordcount':
            args['wordcount'] = value
        elif command == 'coin':
            args['coin'] = value
        else:
            print('invalid input: ' + command  + '\nrun `python3 mnemonic-calculator.py help` for help')
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
    print('Press q to stop')
    
    for cpu in range(args['cpu_count']):
        multiprocessing.Process(target = main, args = (database, args)).start()
