# platformio-air105

PlatformIO platform for Megahunt MH190X (Air105) Cortex-M4 SoC.

## Quick Start

1. Install [PlatformIO](https://platformio.org/)
2. Create a project with `board = air105` or `board = mh1903`
3. Build: `pio run`
4. Upload: `pio run -t upload`

## Requirements

- `arm-none-eabi-gcc` toolchain (installed automatically by PlatformIO)
- `python3` with `pycryptodome` (for mhboot upload protocol)
