# GameTimeTracker

A cross-platform application time tracker that monitors running processes and logs usage time per day.

Note: Tested only on Windows (11) and macOS.

## Setup

### Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv .venv
```

**Windows:**
```cmd
python -m venv .venv
```

### Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running

### Run from Source

**macOS/Linux:**
```bash
source .venv/bin/activate
python3 gtt.py
```

**Windows:**
```cmd
.venv\Scripts\activate.bat
python gtt.py
```

**Stop:** Press `Ctrl+C`

### Build Standalone Executable

**macOS/Linux (using Makefile):**
```bash
make build
```
This will:
1. Create `.venv` if it doesn't exist
2. Install dependencies
3. Build the executable with PyInstaller
4. Clean up build artifacts
5. Place the executable in `dist/gtt`

**Manual build (all platforms):**
```bash
# Activate venv first
pyinstaller --onefile gtt.py
```

The executable will be in the `dist/` folder.

**Run the executable:**
- macOS/Linux: `./dist/gtt`
- Windows: `dist\gtt.exe`

### Clean Build Artifacts

**Manual cleanup:**
```bash
rm -rf build dist __pycache__ *.spec
```

Note: The `build` target automatically cleans up intermediate artifacts.

## Configuration

### Environment Variables

- `GTT_POLL_SEC` - Polling interval in seconds (default: 10)

### Exclusions

Exclusions will be your way of cleaning up everything that are not games/binaries you want to track. This process will be tedious at first, e.g. on my mac, I'm above 500 exclusions, and still new ones appear from time to time.

Create a `exclusions.json` file in the data directory to exclude processes whose names start with the specified prefixes:

**Data Directory Location:**
- macOS: `~/Library/Application Support/GameTimeTracker/`
- Linux: `~/.local/share/GameTimeTracker/`
- Windows: `%APPDATA%\GameTimeTracker\`

**Example `exclusions.json`:**
```json
[
  "Helper",
  "Launcher",
  "Steam"
]
```

### Aliases

You can create an `aliases.json` file in the data directory to map normalized application names to preferred names:

**Example `aliases.json`:**
```json
{
  "unity helper": "Unity Game",
  "chrome": "Google Chrome"
}
```

Aliases are applied **after** the application name is normalized from process information. Both the normalized name and the aliased name are checked against exclusions.

## Export Game Time Data Script

You can export tracked game time data to the [Finished Games](https://github.com/Kartones/finished-games) format using the `export_to_fg_game_time.py` script:

```bash
# Activate venv first
source .venv/bin/activate

python3 export_to_fg_game_time.py queries
```

This generates two files in your data directory (note that you can choose the filename):
- `queries.input` - Game names (one per line)
- `queries.output` - Playtime in minutes (one per line, matching order with the other file)

You can then use these files with the [Finished Games import tools](https://github.com/Kartones/finished-games/blob/3638b7f329094c1c2a6866aed24205d4419b8a11/finishedgames/core/management/commands/import_games_playtime.py#L15).

## Data Storage

Time tracking data is stored as daily JSON files, with seconds precision.
