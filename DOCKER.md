# Running Halo CE Map Downloader with Docker

This project can be run inside a Docker container, avoiding the need to install Python, Chrome, and various dependencies directly on your host machine.

---

## Prerequisites

-   [Docker](https://www.docker.com/) installed and running.
-   Docker Compose (optional, but recommended).

---

## 1. Quick Start with Docker Compose

We provide a `docker-compose.yml` to make running and configuring the downloader as easy as possible.

### Show Help Menu
```bash
docker compose run --rm downloader
```

### Download Multiplayer Maps
```bash
docker compose run --rm downloader -dm
```
This will download maps and place them in the `./downloads` folder on your host machine.

### Automatically Install Maps to Halo CE
To have the script automatically extract and copy `.map` files into your Halo Custom Edition installation directory:

1.  Open `docker-compose.yml`.
2.  Uncomment and configure the volume pointing to your Halo installation directory:
    ```yaml
    volumes:
      - ./downloads:/app/downloads
      - /path/to/your/Halo/CE/Installation:/halo
    ```
3.  Run the downloader specifying `/halo` as the installation directory:
    ```bash
    docker compose run --rm downloader -dm --HaloInstallDir /halo
    ```

---

## 2. Using Docker CLI

If you prefer using standard Docker commands:

### Build the Image
```bash
docker build -t halomaps-downloader .
```

### Run the Downloader (Standard Download)
```bash
docker run --rm -v "$(pwd)/downloads:/app/downloads" halomaps-downloader -dm
```

### Run the Downloader and Auto-Install Maps
```bash
docker run --rm \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "/path/to/your/Halo/CE/Installation:/halo" \
  halomaps-downloader -dm --HaloInstallDir /halo
```

---

## ⚙️ Configuration details

-   **Base Image:** Built using `python:3.12-slim` for a lightweight and secure footprint.
-   **Browser Driver:** Leverages Selenium 4's built-in Selenium Manager to automatically handle the download and configuration of the Chrome WebDriver matching the installed Google Chrome version.
-   **Stability:** Runs Google Chrome in `--headless` mode with `--no-sandbox` and `--disable-dev-shm-usage` flags, resolving common container crash issues.
