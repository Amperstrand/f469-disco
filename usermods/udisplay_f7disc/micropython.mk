DISPLAY_MOD_DIR ?= $(USERMOD_DIR)
REPO_ROOT ?= $(abspath $(USERMOD_DIR)/../..)
SHARED_DISPLAY_DIR := $(REPO_ROOT)/usermods/udisplay_f469
F7_MPY_DIR := $(REPO_ROOT)/micropython

ifeq ($(CMSIS_MCU),STM32F746xx)
SRC_USERMOD += $(DISPLAY_MOD_DIR)/display.c
SRC_USERMOD += $(DISPLAY_MOD_DIR)/lv_stm_hal/lv_stm_hal.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/fonts/square.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/fonts/font_roboto_mono_28.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/fonts/font_roboto_mono_22.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/fonts/font_roboto_mono_16.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/fonts/font_roboto_mono_12.c
SRC_USERMOD += $(SHARED_DISPLAY_DIR)/pixelart/px_img.c
SRC_USERMOD += $(F7_MPY_DIR)/lib/stm32lib/STM32F7xx_HAL_Driver/Src/stm32f7xx_hal_ltdc.c
SRC_USERMOD += $(F7_MPY_DIR)/lib/stm32lib/STM32F7xx_HAL_Driver/Src/stm32f7xx_hal_dma2d.c

LVGL_DIR := $(SHARED_DISPLAY_DIR)
include $(LVGL_DIR)/lvgl/lvgl.mk
SRC_USERMOD += $(CSRCS)
CFLAGS_USERMOD += $(CFLAGS)

CFLAGS_USERMOD += -I$(DISPLAY_MOD_DIR)
CFLAGS_USERMOD += -I$(DISPLAY_MOD_DIR)/lv_stm_hal
CFLAGS_USERMOD += -I$(SHARED_DISPLAY_DIR)
CFLAGS_USERMOD += -I$(SHARED_DISPLAY_DIR)/lvgl
CFLAGS_USERMOD += -I$(SHARED_DISPLAY_DIR)/pixelart
CFLAGS_USERMOD += -I$(F7_MPY_DIR)/ports/stm32
endif
