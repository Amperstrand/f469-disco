include('f7_display.py')
freeze('../libs/common/embit', ('__init__.py', 'base.py', 'misc.py', 'networks.py', 'hashes.py', 'base58.py', 'bech32.py', 'compact.py', 'ec.py', 'bip32.py', 'script.py'))
freeze('../tests', 'f7_specter_crypto.py')
freeze('f7_specter_crypto_boot', 'main.py')
