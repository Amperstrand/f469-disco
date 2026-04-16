HASH_DIR := $(USERMOD_DIR)/../../usermods/uhashlib

SRC_USERMOD += $(HASH_DIR)/crypto/ripemd160.c
SRC_USERMOD += $(HASH_DIR)/crypto/sha2.c
SRC_USERMOD += $(HASH_DIR)/crypto/hmac.c
SRC_USERMOD += $(HASH_DIR)/crypto/pbkdf2.c
SRC_USERMOD += $(HASH_DIR)/crypto/memzero.c
SRC_USERMOD += $(HASH_DIR)/hashlib.c
SRC_USERMOD += $(HASH_DIR)/uhmac.c

CFLAGS_USERMOD += -I$(HASH_DIR)/crypto
