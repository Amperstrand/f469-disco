include('f7_display.py')
freeze('../libs/common', ('embit/__init__.py', 'embit/base.py', 'embit/misc.py', 'embit/networks.py', 'embit/hashes.py', 'embit/base58.py', 'embit/bech32.py', 'embit/compact.py', 'embit/ec.py', 'embit/bip32.py', 'embit/script.py'))
freeze('../tests', 'f7_specter_crypto.py')
freeze('f7_specter_crypto_boot', 'main.py')
