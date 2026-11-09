# The Advanced Cartographer

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-oisin833%2Fthe--advanced--cartographer-blue?logo=docker)](https://hub.docker.com/r/oisin833/the-advanced-cartographer)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()

**The Advanced Cartographer** is an automated tool designed to scrape, download, extract, and optionally install custom maps and community content for **Halo: Custom Edition** directly from [halomaps.org](https://www.halomaps.org/).

The tool uses Selenium 4 with headless Google Chrome for reliable form interaction and link discovery, `requests` for streaming downloads, and Python's built-in archive extraction utilities to manage map placement into your Halo CE installation.

---

## Features

- **Extensive Category Coverage:** Scrapes and downloads multiplayer maps, AI multiplayer, singleplayer custom maps, Machinima maps, Lumoria campaign, custom UIs, and CMT releases.
- **Automated Pagination:** Seamlessly navigates paginated halomaps.org sections to batch-download map archives.
- **Auto-Extraction & Installation:** Automatically extracts `.map` files from downloaded `.zip` archives and installs them directly into your Halo CE `maps/` directory.
- **Safety Checks:** Prevents overwriting existing maps and protects core interface files like `ui.map`.
- **Zero-Setup Docker Option:** Available on [Docker Hub](https://hub.docker.com/r/oisin833/the-advanced-cartographer) with Chrome and dependencies pre-configured.
- **Clean Headless Execution:** Runs Google Chrome in headless mode with low memory overhead.

---

## Quick Start with Docker (Recommended)

Running via Docker eliminates the need to install Python, Chrome, or any dependencies on your system.

### Pull from Docker Hub
```bash
docker pull oisin833/the-advanced-cartographer:latest
```

### Download Maps to Local Directory
```bash
# Linux / macOS:
docker run --rm -v "$(pwd)/downloads:/app/downloads" oisin833/the-advanced-cartographer:latest -dm

# Windows (PowerShell):
docker run --rm -v "${PWD}/downloads:/app/downloads" oisin833/the-advanced-cartographer:latest -dm
```

### Docker Compose
A ready-to-use [`docker-compose.yml`](docker-compose.yml) is included:
```bash
# Show options
docker compose run --rm downloader --help

# Download multiplayer maps
docker compose run --rm downloader -dm
```

For full container instructions, volume configurations, and automated Halo CE installation examples, see **[DOCKER.md](DOCKER.md)**.

---

## Local Installation (Without Docker)

### Prerequisites

- **Python 3.10+**
- **Google Chrome** installed on your host machine
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/OisinHick/The-Advanced-Cartographer.git
cd The-Advanced-Cartographer
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

---

## Command-Line Usage

Run the script from the project directory:

```bash
python HaloCEMapDownloader.py [options]
```

### Available Options

| Short Flag | Long Flag | Description | Paginated |
| :--- | :--- | :--- | :---: |
| `-h` | `--help` | Display the help menu and exit | — |
| | `--HaloInstallDir <path>` | Specify Halo CE installation folder for auto-extract & install | — |
| `-dm` | `--DownloadMultiplayer` | Download multiplayer maps | Yes |
| `-dmai` | `--DownloadMultiplayerWthAI` | Download multiplayer maps with AI | Yes |
| `-dmm` | `--DownloadMultiplayerModified` | Download modified multiplayer maps | Yes |
| `-dmfm` | `--DownloadMultiplayerForMachinima`| Download Machinima multiplayer maps | No |
| `-dlm` | `--DownloadLumoria` | Download Lumoria campaign maps | No |
| `-dsm` | `--DownloadSingleplayerModified` | Download modified singleplayer maps | Yes |
| `-dscm` | `--DownloadSingleplayerCustomMaps`| Download custom singleplayer maps | Yes |
| `-dcui` | `--DownloadCustomUIs` | Download custom UI maps | Yes |
| `-dcms` | `--DownloadCMTMaps` | Download CMT maps (manual install required) | No |

---

## Usage Examples

### 1. Download Only
Files are saved to a local `downloads/` directory:

```bash
# Download all multiplayer maps
python HaloCEMapDownloader.py -dm

# Download custom singleplayer maps
python HaloCEMapDownloader.py -dscm

# Download Lumoria campaign maps
python HaloCEMapDownloader.py -dlm
```

### 2. Download and Automatically Install into Halo CE
Provide `--HaloInstallDir` alongside download flags. The script will download the files, extract any `.map` files into `<HaloInstallDir>/maps`, and clean up the temporary zip files:

```bash
# Windows
python HaloCEMapDownloader.py -dm --HaloInstallDir "C:\Program Files (x86)\Microsoft Games\Halo Custom Edition"

# Linux / Wine
python HaloCEMapDownloader.py -dm --HaloInstallDir "/home/user/.wine/drive_c/Program Files (x86)/Microsoft Games/Halo Custom Edition"
```

> **Requirement:** The directory specified in `--HaloInstallDir` must contain `halo.exe` and a `maps/` subdirectory.

### 3. Install Previously Downloaded Maps
If you already have zip files or `.map` files in your `downloads/` directory, specify `--HaloInstallDir` without download flags to process and install them:

```bash
python HaloCEMapDownloader.py --HaloInstallDir "C:\Program Files (x86)\Microsoft Games\Halo Custom Edition"
```

---

## Important Notes & Troubleshooting

### Special Map Requirements
- **CMT Maps (`-dcms`):** CMT maps rely on external scripts and assets beyond simple `.map` placement. As a result, `--HaloInstallDir` cannot be used with `-dcms`. Download the files and follow CMT's included instructions for manual installation.
- **Lumoria Maps (`-dlm`):** Lumoria campaign maps may require external sound DLLs to be installed into your Halo root directory for audio to function properly.
- **Custom UIs (`-dcui`):** Halo CE requires a UI that includes menu entries for custom maps. By default, the installer will skip replacing `ui.map` if one already exists to prevent overwriting your existing menu setup.

### Common Issues

- **`Halo installation or maps directory not found`:**
  Ensure the path passed to `--HaloInstallDir` is the root Halo Custom Edition folder containing `halo.exe`, and ensure a `maps/` subfolder exists inside it.
- **`TimeoutError`:**
  Indicates network latency or halomaps.org server responsiveness issues. Retry the command.
- **Browser/Driver Initialization Issues (Local execution):**
  Ensure Google Chrome is updated to a modern version. Selenium 4 manages the required ChromeDriver automatically. Alternatively, run via Docker to bypass host browser configuration.

---

## Contributing

Contributions, bug reports, and suggestions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/OisinHick/The-Advanced-Cartographer).
