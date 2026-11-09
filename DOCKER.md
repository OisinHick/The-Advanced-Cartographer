# Running The Advanced Cartographer with Docker

Run **The Advanced Cartographer** inside a Docker container without needing to manually install Python, Google Chrome, or browser drivers on your host system.

The official container image is published on Docker Hub:
**[`oisin833/the-advanced-cartographer`](https://hub.docker.com/r/oisin833/the-advanced-cartographer)**

---

## 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+ recommended)
- [Docker Compose](https://docs.docker.com/compose/) (included with Docker Desktop on Windows/macOS, or Docker Compose V2 on Linux)

---

## 2. Quick Start with Docker Compose (Recommended)

A preconfigured [`docker-compose.yml`](docker-compose.yml) is included in this repository.

### Display the Help Menu
```bash
docker compose run --rm downloader
```

### Download Maps to Host
By default, files are downloaded directly into `./downloads` on your host machine:

- **Multiplayer Maps:**
  ```bash
  docker compose run --rm downloader -dm
  ```

- **Singleplayer Custom Maps:**
  ```bash
  docker compose run --rm downloader -dscm
  ```

- **Multiplayer Maps with AI:**
  ```bash
  docker compose run --rm downloader -dmai
  ```

### Automatically Download & Install to Halo Custom Edition

1. Open [`docker-compose.yml`](docker-compose.yml).
2. Uncomment the Halo installation volume line and set it to your host's Halo CE path:
   ```yaml
   volumes:
     - ./downloads:/app/downloads
     - C:\Program Files (x86)\Microsoft Games\Halo Custom Edition:/halo   # Windows example
     # or for Linux/Wine:
     # - /home/user/.wine/drive_c/Program Files (x86)/Microsoft Games/Halo Custom Edition:/halo
   ```
3. Run the container specifying `/halo` as the `--HaloInstallDir`:
   ```bash
   docker compose run --rm downloader -dm --HaloInstallDir /halo
   ```
   The container will download the archives, extract `.map` files directly into your Halo CE `maps/` directory (skipping duplicates and `ui.map`), and clean up downloaded archives upon completion.

---

## 3. Using the Docker CLI (Direct `docker run`)

You do not need to clone the repository to run the container. You can run the official pre-built image directly from Docker Hub:

### Pull the Image
```bash
docker pull oisin833/the-advanced-cartographer:latest
```

### Show Help
```bash
docker run --rm oisin833/the-advanced-cartographer:latest --help
```

### Download Maps

**Linux / macOS (Bash / Zsh):**
```bash
docker run --rm -v "$(pwd)/downloads:/app/downloads" oisin833/the-advanced-cartographer:latest -dm
```

**Windows (PowerShell):**
```powershell
docker run --rm -v "${PWD}/downloads:/app/downloads" oisin833/the-advanced-cartographer:latest -dm
```

**Windows (Command Prompt):**
```cmd
docker run --rm -v "%cd%/downloads:/app/downloads" oisin833/the-advanced-cartographer:latest -dm
```

### Download and Auto-Install Directly to Halo CE

Mount your host Halo directory into `/halo` inside the container:

**Linux / macOS:**
```bash
docker run --rm \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "/path/to/halo/ce:/halo" \
  oisin833/the-advanced-cartographer:latest -dm --HaloInstallDir /halo
```

**Windows (PowerShell):**
```powershell
docker run --rm `
  -v "${PWD}/downloads:/app/downloads" `
  -v "C:\Program Files (x86)\Microsoft Games\Halo Custom Edition:/halo" `
  oisin833/the-advanced-cartographer:latest -dm --HaloInstallDir /halo
```

---

## 4. Building the Image from Source

If you prefer building the image locally from source:

```bash
# Clone the repository
git clone https://github.com/OisinHick/The-Advanced-Cartographer.git
cd The-Advanced-Cartographer

# Build the image
docker build -t oisin833/the-advanced-cartographer:latest .
```

Or using Docker Compose:
```bash
docker compose build
```

---

## 5. Technical & Runtime Details

- **Base Image:** Built on `python:3.12-slim` for a lightweight and secure container footprint.
- **Chrome & Driver Management:** Installs the official `google-chrome-stable` package and utilizes Selenium 4's built-in **Selenium Manager** to dynamically match and provision ChromeDriver.
- **Headless Execution:** Pre-configured with `--headless`, `--no-sandbox`, `--disable-gpu`, and `--disable-dev-shm-usage` flags for stable, headless browser execution in restricted container environments.
- **Volume Permissions:** The internal `/app/downloads` directory is set to permissive access (`chmod 777`) to avoid volume permission issues when mounting local host directories across diverse host operating systems and user IDs.
