TARGET_DIR = bin
BOARD ?= STM32F7DISC
USER_C_MODULES ?= ../../../usermods
MPY_DIR ?= micropython
FROZEN_MANIFEST_EMPTY ?= ../../../manifests/empty.py
FROZEN_MANIFEST_FULL ?= ../../../manifests/disco.py
FROZEN_MANIFEST_F7_EMPTY ?= ../../../manifests/f7_empty.py
FROZEN_MANIFEST_F7 ?= ../../../manifests/f7.py
FROZEN_MANIFEST_F7_DISPLAY ?= ../../../manifests/f7_display.py
FROZEN_MANIFEST_F7_TEST ?= ../../../manifests/f7_display_test.py
FROZEN_MANIFEST_F7_SPECTER ?= ../../../manifests/f7_specter_demo.py
FROZEN_MANIFEST_F7_SPECTER_CRYPTO ?= ../../../manifests/f7_specter_crypto.py
FROZEN_MANIFEST_F7_SPECTER_EXTERNAL_POC ?= ../../../manifests/f7_specter_external_poc.py
FROZEN_MANIFEST_UNIX ?= ../../../manifests/unix.py
DEBUG ?= 0
SPECTER_DIY_DIR ?= $(abspath ../specter-diy)

F7_CFLAGS_EXTRA = -DMODULE_DISPLAY_ENABLED=1 -DMODULE_SECP256K1_ENABLED=1 -DMODULE_HASHLIB_ENABLED=1 -DMODULE_QRCODE_ENABLED=1

# Derive output artifact name from BOARD
BOARD_LC := $(shell echo $(BOARD) | tr '[:upper:]' '[:lower:]')
BUILD_DIR = $(MPY_DIR)/ports/stm32/build-$(BOARD)

$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

# check submodules
$(MPY_DIR)/mpy-cross/Makefile:
	git submodule update --init --recursive

# cross-compiler
mpy-cross: $(TARGET_DIR) $(MPY_DIR)/mpy-cross/Makefile
	@echo "Building cross-compiler"
	make -C $(MPY_DIR)/mpy-cross \
	CFLAGS_EXTRA="-Wno-error" \
	DEBUG=$(DEBUG) && \
	cp $(MPY_DIR)/mpy-cross/mpy-cross $(TARGET_DIR)

# Minimal firmware for any supported STM32 board (no usermods, no frozen libs)
board-minimal: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building minimal firmware for $(BOARD)
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(BUILD_DIR)/firmware.elf \
		$(TARGET_DIR)/upy-$(BOARD_LC)-minimal.bin

# F746G-DISCO minimal firmware (no usermods, no frozen libs)
f7-minimal: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO minimal firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(BUILD_DIR)/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-minimal.bin

# F746G-DISCO with usermods but no frozen libs (for testing usermod compilation)
f7-empty: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo "Building F746G-DISCO with usermods, no frozen libs"
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_EMPTY) \
		CFLAGS_EXTRA="$(F7_CFLAGS_EXTRA)" \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-empty.bin

# F746G-DISCO with usermods and frozen bitcoin library
f7: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO full firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7) \
		CFLAGS_EXTRA="$(F7_CFLAGS_EXTRA)" \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc.bin

# F746G-DISCO display-only bring-up firmware
f7-display: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO display bring-up firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_display \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_DISPLAY) \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1" \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-display.bin

# F746G-DISCO display+DMA2D+touch test firmware (auto-runs on boot)
f7-test: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO display test firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_display \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_TEST) \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1" \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-test.bin

f7-specter-demo: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO Specter demo firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_display \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_SPECTER) \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1" \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-specter-demo.bin

f7-portrait-smoke: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO portrait smoke firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_display \
		FROZEN_MANIFEST=../../../manifests/f7_portrait_smoke.py \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1 -DDISABLE_NETWORK=1" \
		MICROPY_SSL_MBEDTLS=0 \
		MICROPY_PY_USSL=0 \
		MICROPY_PY_LWIP=0 \
		LD_FILES="boards/stm32f746_crypto.ld boards/common_ifs.ld" \
		TEXT1_ADDR= \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-portrait-smoke.bin

# F746G-DISCO Specter crypto demo (display + secp256k1 + embit, no networking to save flash)
f7-specter-crypto: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO Specter crypto firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_specter \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_SPECTER_CRYPTO) \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1 -DMODULE_SECP256K1_ENABLED=1 -DMODULE_HASHLIB_ENABLED=1 -DMODULE_QRCODE_ENABLED=1 -DDISABLE_NETWORK=1 -DCRYPTO_BUILD=1" \
		MICROPY_SSL_MBEDTLS=0 \
		MICROPY_PY_USSL=0 \
		MICROPY_PY_LWIP=0 \
		LD_FILES="boards/stm32f746_crypto.ld boards/common_ifs.ld" \
		TEXT1_ADDR= \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-specter-crypto.bin

f7-specter-external-poc: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building F746G-DISCO external Specter PoC firmware
	SPECTER_DIY_DIR="$(SPECTER_DIY_DIR)" make -C $(MPY_DIR)/ports/stm32 \
		BOARD=STM32F7DISC \
		USER_C_MODULES=../../../usermods_f7_specter \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_F7_SPECTER_EXTERNAL_POC) \
		CFLAGS_EXTRA="-DMODULE_DISPLAY_ENABLED=1 -DMODULE_HASHLIB_ENABLED=1 -DDISABLE_NETWORK=1 -DCRYPTO_BUILD=1" \
		MICROPY_SSL_MBEDTLS=0 \
		MICROPY_PY_USSL=0 \
		MICROPY_PY_LWIP=0 \
		LD_FILES="boards/stm32f746_crypto.ld boards/common_ifs.ld" \
		TEXT1_ADDR= \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F7DISC/firmware.elf \
		$(TARGET_DIR)/upy-f7disc-specter-external-poc.bin

# Legacy F469 targets (still work with explicit BOARD=STM32F469DISC)
empty: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building binary without frozen files
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_EMPTY) \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(BUILD_DIR)/firmware.elf \
		$(TARGET_DIR)/upy-$(BOARD_LC)-empty.bin

disco: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building binary with frozen files
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_FULL) \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(BUILD_DIR)/firmware.elf \
		$(TARGET_DIR)/upy-$(BOARD_LC).bin

# unixport (simulator)
unix: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/unix
	@echo Building binary with frozen files
	make -C $(MPY_DIR)/ports/unix \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_UNIX) && \
	cp $(MPY_DIR)/ports/unix/micropython $(TARGET_DIR)/micropython_unix

simulate: unix
	$(TARGET_DIR)/micropython_unix

test: unix
	$(TARGET_DIR)/micropython_unix tests/run_tests.py

# Flash the most recently built firmware for the board
flash: 
	@echo "Flashing $(TARGET_DIR)/upy-$(BOARD_LC)-*.bin via st-flash"
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-$(BOARD_LC)-minimal.bin 0x08000000 || \
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-$(BOARD_LC)-empty.bin 0x08000000 || \
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-$(BOARD_LC).bin 0x08000000

# Flash F7 minimal
flash-f7-minimal:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-minimal.bin 0x08000000

flash-f7-empty:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-empty.bin 0x08000000

flash-f7:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc.bin 0x08000000

flash-f7-display:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-display.bin 0x08000000

flash-f7-test:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-test.bin 0x08000000

flash-f7-specter-demo:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-specter-demo.bin 0x08000000

flash-f7-specter-crypto:
	st-flash --connect-under-reset --reset write $(TARGET_DIR)/upy-f7disc-specter-crypto.bin 0x08000000

all: mpy-cross f7-minimal f7-empty f7 unix

clean:
	rm -rf $(TARGET_DIR)
	make -C $(MPY_DIR)/mpy-cross clean
	make -C $(MPY_DIR)/ports/unix \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_UNIX) clean
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		USER_C_MODULES=$(USER_C_MODULES) clean

.PHONY: all clean
