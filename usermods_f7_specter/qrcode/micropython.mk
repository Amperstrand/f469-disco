QR_MOD_DIR := $(USERMOD_DIR)/../../usermods/qrcode

SRC_USERMOD += $(QR_MOD_DIR)/qrcodegen/qrcodegen.c
SRC_USERMOD += $(QR_MOD_DIR)/qrcode.c

CFLAGS_USERMOD += -I$(QR_MOD_DIR)/qrcodegen
