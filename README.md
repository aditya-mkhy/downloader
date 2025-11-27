# Downloader

A smart Python-based file downloader that can **resume broken or paused downloads** automatically — even after a day or using a refreshed link.  
It reads links from a `link.txt` file and manages each download intelligently.

> Built to solve one major browser issue: resuming failed downloads **without losing progress**.
<br>

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
<br>

## Features

-  **Resume broken downloads** — continues from where it left off.  
-  **Reads links from `link.txt`** — no need to manually enter URLs every time.  
-  **Auto cleanup** — removes completed links from the list if enabled.  
-  **File name detection** — automatically extracts filename from headers or URLs.  
-  **Chunked download system** — saves in parts and merges efficiently.  
-  **Connection check** — automatically verifies internet before downloading.  
-  **Time & data tracking** — logs size, speed, and elapsed time.  
-  **Lightweight multithreaded design** — uses `Thread` for write operations.  
<br>

## Project structure

```
downloader/
├─ down.py        # main download logic
├─ util.py        # helper utilities (logging, path, status, etc.)
├─ delete.py      # removes finished links from link.txt
├─ link.txt       # list of links to download
├─ LICENSE
├─ README.md
```
<br>

## Requirements

- Python **3.8 or newer**
- Libraries:
  ```bash
  pip install requests
  ```
<br>

## How It Works

1. Add one or more download URLs into `link.txt`, one per line:
   ```
   https://example.com/file1.zip
   https://example.com/video.mp4
   ```

2. Run the script:
   ```bash
   python down.py
   ```

3. The program will:
   - Check your connection.
   - Detect the filename automatically.
   - Create a partial file if download stops midway.
   - Resume download next time you run it.

4. Once download completes (if `del_link=True` is set), the tool removes that link from `link.txt`.
<br>

## Usage Example

### Basic

```python
from down import Downloader

# Create downloader instance
dl = Downloader()
# download path
dl.save_path = "D:\\Downloads"
# Start download of all URLs in link.txt
dl.run()
```
<br>

## Utilities

### util.py includes:
- `get_downloadpath()` → Auto returns system Downloads folder  
- `is_online()` → Checks network connection  
- `time_cal()` → Converts seconds to readable time  
- `data_size_cal()` → Converts bytes to MB/GB  
- `log()` → Timestamps log output  
<br>

## Auto-cleanup system

- Each completed link is **removed** from `link.txt` using `delete.py`.
- If any line is invalid or already deleted, the tool skips gracefully.
<br>

## Tips

- You can close the app anytime; when reopened, it will resume unfinished downloads.
- Works great for large files (ISO, MP4, ZIP, etc.).
- Supports **multiple concurrent threads** for writing and downloading.
- If a link requires renewal, replace it in `link.txt` with the new one — the downloader will continue the same partial file.
<br>

## Safety Notes

- The tool **never executes** or opens downloaded files — only saves them.  
- No remote code, subprocess, or hidden execution is performed.
- You can inspect logs printed in console for detailed progress.
<br>

## Developer Notes

- `down.py` — core logic, handles streaming, retries, resuming, and headers.  
- `delete.py` — parses and rewrites `link.txt` for link removal.  
- `util.py` — helper functions for time, size, connection, and logs.

<br>

## License

This project is licensed under the **MIT License**.  
Feel free to use, modify, and share it.

<br>

## Credits

Created to fix the everyday pain of interrupted downloads.  
Developed with ❤️ in Python.
