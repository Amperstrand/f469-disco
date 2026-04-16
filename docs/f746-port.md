# STM32F746G-DISCO port checkpoint

This document records the current known-good checkpoint for the STM32F746G-DISCO port.

## Hardware-tested working state

Validated on real STM32F746G-DISCO hardware:

- `make f7-specter-crypto` builds and flashes successfully
- Display init is stable
- Touch input works on the crypto home screen
- The home screen shows the three-button Specter-style flow:
  - `Receive`
  - `Master XPUB`
  - `Sign Test`
- The crypto stack is live on-device:
  - `secp256k1` C module
  - frozen `embit` Python modules
  - custom `hashlib` / `hmac` usermods

## Build and flash

```bash
make f7-specter-crypto
make flash-f7-specter-crypto
```

Artifacts:

- `bin/upy-f7disc-specter-crypto.bin`

## Important implementation details

This checkpoint depends on a few F746-specific fixes:

- `MODULE_HASHLIB_ENABLED=1` is required so the F746 crypto build exposes the custom `hashlib` and `hmac` modules expected by `embit`
- the frozen manifest must preserve the `embit/...` namespace, otherwise `from embit import ...` fails at runtime
- the FT5336 touch controller must stay in its default mode; forcing polling mode prevented reliable LVGL release events on this board
- the crypto UI uses direct LVGL event callbacks and keeps the active screen alive in Python state

## Current scope

This is a working crypto/demo checkpoint, not the full Specter-DIY application yet.

What is already proven on F746:

- display
- touch
- LVGL screen flow
- real HD key derivation
- real address generation
- real signing path

What remains for the next milestone:

- replace the checkpoint UI shell with more of the real Specter-DIY application flow
- preserve this checkpoint as the recovery target if later experiments regress boot or touch handling

## Debug helper

The F746 display module now exposes `display.touch_point()` for low-level touch debugging when needed.
