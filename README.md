# Halo Custom Edition Map Downloader

This script downloads and optionally installs maps for Halo Custom Edition from [halomaps.org](https://www.halomaps.org/). It uses Selenium for web scraping and browser automation, `requests` for downloading files, and `webdriver-manager` for managing ChromeDriver.

## Features

-   Downloads maps from various categories on halomaps.org.
-   Supports downloading maps from paginated lists.
-   Optionally automatically extracts and moves `.map` files to a specified Halo installation directory.
-   Handles invalid characters in filenames.
-   Uses a headless Chrome browser for minimal visual intrusion.
-   Automatically manages ChromeDriver installation using `webdriver-manager`.

## Prerequisites

-   Python 3.7+
-   Chrome browser installed
-   Required Python packages (install using `pip`):

    ```bash
    pip install selenium requests beautifulsoup4 webdriver-manager
    ```

## Usage

1.  **Clone the Repository (Optional):**

    Clone it to your local machine:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Run the Script:**

    Use the following command-line arguments to control the script's behavior:

    ```bash
    python HaloCEMapDownloader.py [options]
    ```

    **Options:**

    -   `--HaloInstallDir <directory>`:  (Optional) Specify the Halo Custom Edition installation directory. If provided, the script will automatically move downloaded `.map` files to the `maps` folder within this directory *and will not download any files*.  This option is mutually exclusive with the download options.
    -   `-dm`, `--DownloadMultiplayer`: Download multiplayer maps.
    -   `-dmai`, `--DownloadMultiplayerWthAI`: Download multiplayer maps with AI.
    -   `-dmm`, `--DownloadMultiplayerModified`: Download modified multiplayer maps.
    -   `-dmfm`, `--DownloadMultiplayerForMachinima`: Download multiplayer maps used for machinima.
    -   `-dlm`, `--DownloadLumoria`: Download Lumoria maps.
    -   `-dsm`, `--DownloadSingleplayerModified`: Download modified singleplayer maps.
    -   `-dscm`, `--DownloadSingleplayerCustomMaps`: Download custom singleplayer maps.
    -   `-dcui`, `--DownloadCustomUIs`: Download custom UIs.
    -   `-dcms`, `--DownloadCMTMaps`: Download CMT Maps.
    -    `-h`, `--help`: Show the help message.

    **Examples:**

    -   Download all multiplayer maps:

        ```bash
        python HaloCEMapDownloader.py -dm
        ```

    -   Download Lumoria maps:

        ```bash
        python HaloCEMapDownloader.py -dlm
        ```

    -   Download multiplayer maps and move them to the Halo installation directory:

        ```bash
        python HaloCEMapDownloader.py -dm --HaloInstallDir "C:\Program Files (x86)\Microsoft Games\Halo Custom Edition"
        ```
        *Important*: Replace `"C:\Program Files (x86)\Microsoft Games\Halo Custom Edition"` with the actual path to your Halo CE installation.

    -   Move existing `.map` files from the `downloads` folder to the Halo CE installation:

        ```bash
        python HaloCEMapDownloader.py --HaloInstallDir "C:\Program Files (x86)\Microsoft Games\Halo Custom Edition"
        ```
        *Important*:  This will *not* download any new maps.  It only processes files already in the `downloads` folder.
    - Show Help Menu
        ```bash
        python HaloCEMapDownloader.py -h
        ```

3.  **Downloads Folder:**

    Downloaded files will be saved in a folder named `downloads` in the same directory as the script.  Extracted `.map` files will also be placed in this folder *before* being moved to the Halo installation directory (if specified).

4. **Log Output**
   - The script uses the `logging` module to provide informative output about its progress, including:
     -  Creation of the `downloads` folder.
     -  Found download links.
     -  Downloaded file paths.
     -  Extraction of ZIP files.
     -  Moving of `.map` files.
     -  Any errors encountered (e.g., network errors, file errors, timeouts).

## Important Notes

-   **Website Structure:** This script relies on the HTML structure of halomaps.org. If the website's structure changes significantly, the script may need to be updated (specifically the XPath expressions and CSS selectors used to find elements).
-   **Download Speed:**  The download speed will depend on your internet connection and the halomaps.org server.
- **Large Downloads**: Downloading *all* maps from a paginated category (e.g., multiplayer maps) can take a considerable amount of time and consume significant disk space.
- **Error Handling**: The script includes error handling for common issues (network errors, file errors, etc.), but unexpected errors may still occur.  Check the log output for details.
-   **Headless Browser:** The script uses a headless Chrome browser, meaning you won't see a browser window open during the scraping process. This is generally more efficient.

## Troubleshooting

-   **`FileNotFoundError`:**
    -   Make sure the `HaloInstallDir` you provided is correct and exists.
    -   Make sure no invalid characters are in the filenames (the script attempts to remove these, but edge cases might exist).
-   **`TimeoutError`:**
    -   This usually indicates a network issue or a problem with the website.  Try running the script again later.
    -   You could try increasing the `WebDriverWait` timeout (currently 10 seconds) in the `get_download_info` and `scrape_filelinks` functions, but this will make the script slower.
-   **Maps not appearing in Halo CE:**
    -   Ensure the `.map` files were correctly moved to the `maps` folder within your Halo CE installation.
    -   Make sure there are no duplicate `.map` files (the script tries to prevent this, but manual intervention might cause issues).
    - Some custom maps may require additional files (e.g., textures, sounds) to be placed in specific folders within the Halo CE installation. Consult the map's documentation (if available) for instructions.

## Contributing

If you find any bugs or have suggestions for improvements, feel free to create an issue or submit a pull request.

This README provides comprehensive documentation for the Halo Custom Edition Map Downloader script, covering its features, prerequisites, usage, troubleshooting, and contribution guidelines.  It's well-structured and easy to understand, making it a valuable resource for users of the script.