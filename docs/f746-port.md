# STM32F746G-DISCO port checkpoint

This document records the current checkpoint for the STM32F746G-DISCO port.

## Hardware-tested working state

Validated on real STM32F746G-DISCO hardware:

- `make f7-specter-crypto` builds and flashes successfully
- Display init is stable
- Touch input works on the crypto home screen
- The port has a stable known-good recovery checkpoint with the three-button crypto home screen:
  - `Receive`
  - `Master XPUB`
  - `Sign Test`
- The crypto stack is live on-device:
  - `secp256k1` C module
  - frozen `embit` Python modules
  - custom `hashlib` / `hmac` usermods

## Current execution checkpoint

The active F746 target now boots a Specter-style menu/navigation flow adapted from `docs/tutorial/4_miniwallet/main.py` in a logical portrait mode (`272x480`) on top of the fixed 480x272 panel.

This keeps the proven F746 LTDC/touch hardware bring-up path while rotating the LVGL logical coordinate space so the UI more closely resembles the original F469 Specter-DIY feel.

The current focus after enabling portrait mode is UI polish: using the full 272x480 logical space so the active screens feel vertically native instead of like compressed landscape layouts.

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
- low-level LTDC panel timing is intentionally left unchanged; portrait mode is implemented by rotating LVGL flush/touch coordinates on top of the fixed 480x272 panel

## Current scope

This is not the full Specter-DIY application yet.

What is already proven on F746:

- display
- touch
- LVGL screen flow
- real HD key derivation
- real address generation
- real signing path
- a real Specter-style top-level menu/navigation flow can fit and build on F746 without disturbing the proven hardware layer
- a portrait-style logical UI can be layered on top of the fixed F746 panel path

What remains for the next milestone:

- hardware-validate the new portrait Specter-style menu flow on F746
- replace more of the temporary menu/adaptation code with real Specter-DIY application flow
- preserve the original three-button crypto screen as the recovery target if later experiments regress boot or touch handling

### Next concrete milestone

Boot and validate the portrait Specter-style application entry/menu flow on STM32F746G-DISCO using the current hardware-tested F746 platform layer.

Success criteria:

- firmware still builds with `make f7-specter-crypto`
- board still boots reliably on hardware
- display and touch behavior do not regress
- the checkpoint three-button shell is replaced by the portrait Specter-style top-level menu/navigation flow adapted from the repo's miniwallet app
- app integration changes stay above the proven F746 display/touch/crypto layer as much as possible

Non-goals for that milestone:

- PSBT signing completeness
- QR scanning/camera integration
- storage/SD-card polish
- large architectural changes to the proven F746 hardware layer
- LTDC timing changes or native panel-mode changes

## Debug helper

The F746 display module now exposes `display.touch_point()` for low-level touch debugging when needed.
