# mnemonic-calculator

A Bitcoin wallet address generator that brute forces random wallet addresses based on the BIP39 Mnemonic wordset.

# Dependencies

<a href="https://www.python.org/downloads/">Python 3.9</a> or higher

Python modules listed in <a href="/requirements.txt">requirements.txt</a>:
- `hdwallet` — HD wallet key and address derivation
- `mnemonic` — BIP39 mnemonic phrase generation
- `bip_utils` — BIP39 seed generation

# Installation

```
git clone https://github.com/ManMallard/mnemonic-calculator.git mnemonicalc
```
```
cd mnemonicalc && pip install -r requirements.txt
```

# Quick Start

```
python3 mnemonic-calculator.py
```

# How It Works

The program continuously generates random BIP39 mnemonic phrases (24 words by default) in a configurable language. Each mnemonic is passed through `bip_utils.Bip39SeedGenerator` to derive a seed, which is then fed into `hdwallet` to derive a P2PKH Bitcoin address.

A pre-calculated offline database of funded P2PKH Bitcoin addresses is included in this project. The last `substring` characters of each generated address are compared against the database. If a match is detected, the full address list is checked for confirmation, and confirmed matches are written to `mnemonic.txt`.

All generated mnemonic/address pairs are continuously appended to `addresses.txt`.

The program uses `multiprocessing.Process()` to run one concurrent worker per CPU core.

# Database FAQ

Visit <a href="/database/">/database</a> for information about the offline address database.

# Parameters

All parameters are passed as `key=value` pairs.

**help**: `python3 mnemonic-calculator.py help=1`  
Prints a short explanation of the parameters.

**time**: `python3 mnemonic-calculator.py time=1`  
Generates a single address and prints how long it took — used for speed testing.

**verbose**: `0` or `1` (default `0`)  
When `1`, every generated Bitcoin address is printed to the terminal. May slow the program down. When `0`, runs silently.

**substring**: integer 1–26 (default `8`)  
Only the last `<substring>` characters of each address are loaded from the database, reducing RAM usage. Smaller values use less memory but raise false-positive probability. False-negative rate is unaffected.

**cpu_count**: integer (default: all available cores)  
Number of parallel processes. More cores = faster generation but higher resource usage.

**wordcount**: integer (default `24`)  
Number of words in each generated mnemonic phrase.

**language**: string (default `english`)  
BIP39 wordlist language. Options: `english`, `spanish`, `french`, `italian`, `portuguese`, `czech`, `japanese`, `korean`, `chinese_simplified`, `chinese_traditional`.

**triedvalues**: file path (default `triedpassphrases.txt`)  
File used to track previously tried passphrases.

**coin**: string (default `BTC`)  
Target coin symbol.

Default run:
```
python3 mnemonic-calculator.py verbose=0 substring=8 language=english wordcount=24 coin=BTC
```

# Expected Output

Every generated mnemonic/address pair is appended to `addresses.txt`:

```
word1 word2 word3 ... word24, 1ExampleBitcoinAddress
```

If a funded address is confirmed, details are written to `mnemonic.txt`.
