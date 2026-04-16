# Build Guide

## Development Environment

### Nix Flake + direnv (Recommended)

Requires Nix >=2.7 with flakes enabled and direnv.

```bash
cd f469-disco
direnv allow
```

Environment activates automatically on entering the directory.

### nix-shell

```bash
nix develop
# or for legacy nix:
nix-shell
```

### Manual Setup

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install gcc-arm-none-eabi binutils-arm-none-eabi python3 libsdl2-dev
```

**macOS:**
```bash
brew tap ArmMbed/homebrew-formulae
brew install arm-none-eabi-gcc python3 sdl2
```

## Submodules

Initialize submodules (done automatically by make):
```bash
git submodule update --init --recursive
```

## Build Commands

```bash
make mpy-cross   # build cross-compiler (required first)
make disco       # firmware with frozen bitcoin lib → bin/upy-f469disco.bin
make empty       # minimal firmware → bin/upy-f469disco-empty.bin
make f7-specter-demo    # F746 display + touch demo → bin/upy-f7disc-specter-demo.bin
make f7-specter-crypto  # F746 crypto checkpoint → bin/upy-f7disc-specter-crypto.bin
make unix        # simulator → bin/micropython_unix
make test        # run tests
make simulate    # run simulator
make clean       # clean build artifacts
make all         # build everything
```

## Output Files

All binaries output to `bin/`:
- `upy-f469disco.bin` - full firmware
- `upy-f469disco-empty.bin` - minimal firmware
- `upy-f7disc-specter-demo.bin` - STM32F746G-DISCO display/touch demo firmware
- `upy-f7disc-specter-crypto.bin` - STM32F746G-DISCO hardware-tested crypto checkpoint
- `micropython_unix` - simulator binary
