"""Application identification and process tracking."""

import plistlib
import psutil
import re
import sys
from pathlib import Path

# Pattern to detect helper processes inside macOS .app bundles
MAC_HELPER_PAT = re.compile(r"\.app/Contents/(MacOS|Helpers|Library)/", re.IGNORECASE)

# Cache for normalized app names: (exe_path, proc_name) -> normalized_name
NORMALIZED_NAMES_CACHE: dict[tuple[str, str], str] = {}


def _macos_app_display_name_from_exe(exe_path: str) -> str | None:
    """
    Given an executable path inside an .app bundle, return CFBundleDisplayName/Name.
    """
    if not exe_path:
        return None

    # Find enclosing *.app
    parts = Path(exe_path).parts
    try:
        idx = next(i for i, seg in enumerate(parts) if seg.lower().endswith(".app"))
    except StopIteration:
        # not inside a bundle
        return None
    app_root = Path(*parts[: idx + 1])
    info_plist = app_root / "Contents" / "Info.plist"
    try:
        with info_plist.open("rb") as file_handle:
            info = plistlib.load(file_handle)
        # Preference order
        for key in ("CFBundleDisplayName", "CFBundleName", "CFBundleExecutable"):
            value = info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    except Exception:
        # fallback to "Game.app" -> "Game"
        return app_root.stem

    return app_root.stem


def _windows_file_product_name(exe_path: str) -> str | None:
    """
    Returns ProductName or FileDescription from version resource.
    Requires pywin32 on Windows.
    """
    if sys.platform != "win32":
        return None
    try:
        import win32api  # type: ignore
    except Exception:
        return None
    try:
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        # Find a suitable translation
        translations = info.get("VarFileInfo", {}).get("Translation", [])
        pairs = [(t[0], t[1]) for t in translations] or [(0x0409, 1200)]  # en-US default

        def query(name):
            for lang, codepage in pairs:
                sub_block = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\{name}"
                try:
                    value = win32api.VerQueryValue(info, sub_block)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                except Exception:
                    pass
            return None

        return query("ProductName") or query("FileDescription")
    except Exception:
        return None


def _normalized_app_name(exe_path: str, proc_name: str) -> str:
    """
    Cross-platform normalization with fallbacks.
    Uses an in-memory cache to avoid repeated lookups.
    """
    cache_key = (exe_path, proc_name)
    if cache_key in NORMALIZED_NAMES_CACHE:
        return NORMALIZED_NAMES_CACHE[cache_key]

    # macOS: prefer bundle name
    if sys.platform == "darwin":
        if exe_path and MAC_HELPER_PAT.search(exe_path):
            name = _macos_app_display_name_from_exe(exe_path)
            if name:
                NORMALIZED_NAMES_CACHE[cache_key] = name
                return name
        # If the binary itself is the bundle's main executable, still try
        name = _macos_app_display_name_from_exe(exe_path)
        if name:
            NORMALIZED_NAMES_CACHE[cache_key] = name
            return name

    # Windows: use version resource if present
    if sys.platform == "win32":
        name = _windows_file_product_name(exe_path)
        if name:
            NORMALIZED_NAMES_CACHE[cache_key] = name
            return name

    # Generic fallbacks
    result = proc_name or exe_path
    if exe_path:
        # "Game.exe" -> "Game"
        base = Path(exe_path).stem
        if base:
            result = base

    if not result:
        result = "unknown"

    NORMALIZED_NAMES_CACHE[cache_key] = result
    return result


def _proc_identity(proc: psutil.Process, exclude_substrings: list[str], aliases: dict[str, str]) -> str | None:
    """
    Extract a normalized identity from a process, applying exclusions and aliases.
    - Exclusions allow for partial matches at the start of the name.
    - Aliases map normalized names (exact match) to preferred forms.
    """
    try:
        name = proc.name() or ""
        if any(name.startswith(prefix) for prefix in exclude_substrings):
            return None
        exe = ""

        try:
            exe = proc.exe() or ""
        except (psutil.AccessDenied, psutil.ZombieProcess):
            pass

        normalized_name = _normalized_app_name(exe, name)
        if not normalized_name:
            return None

        normalized_name = normalized_name.lower()
        # aliases are already lowercased
        normalized_name = aliases.get(normalized_name, normalized_name)

        # exclusions are already lowercased
        if any(normalized_name.startswith(prefix) for prefix in exclude_substrings):
            return None

        return normalized_name
    except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
        return None


def list_running_identities(exclude_substrings: list[str], aliases: dict[str, str]) -> set[str]:
    """
    Return a set of normalized application identities currently running.
    """
    identities = set()
    for process in psutil.process_iter(attrs=[], ad_value=None):
        identity = _proc_identity(process, exclude_substrings, aliases)
        if identity:
            identities.add(identity)
    return identities
