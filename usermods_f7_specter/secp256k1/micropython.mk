SECP_DIR := $(USERMOD_DIR)/../../usermods/secp256k1

SRC_USERMOD += $(SECP_DIR)/mpy/config/secp256k1_build.c
SRC_USERMOD += $(SECP_DIR)/mpy/config/ext_callbacks.c
SRC_USERMOD += $(SECP_DIR)/mpy/libsecp256k1.c

CFLAGS_USERMOD += -I$(SECP_DIR)/secp256k1 -I$(SECP_DIR)/secp256k1/src -I$(SECP_DIR)/mpy/config -DHAVE_CONFIG_H -Wno-unused-function -Wno-error -DMODULE_SECP256K1_ENABLED=1
