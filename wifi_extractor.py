import subprocess
import re
import os
import sys
from datetime import datetime


def run_command(cmd):
    """Run a shell command and return stdout as text."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        return result.stdout
    except Exception as e:
        return f"ERROR: {e}"


def get_wifi_profiles():
    """Return a list of saved Wi-Fi profile names."""
    output = run_command("netsh wlan show profiles")
    profiles = re.findall(r"All User Profile\s*:\s*(.+)", output)
    return [p.strip() for p in profiles]


def get_wifi_password(profile):
    """Return the plain-text key for a given profile, or None."""
    output = run_command(f'netsh wlan show profile name="{profile}" key=clear')
    match = re.search(r"Key Content\s*:\s*(.+)", output)
    if match:
        return match.group(1).strip()
    return None


def get_desktop_path():
    """Return the Desktop folder of the current user (handles OneDrive redirect)."""
    # Prefer the OS-known Desktop location (works even if redirected to OneDrive)
    try:
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        # CSIDL_DESKTOPDIRECTORY = 0x10
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf)
        if buf.value:
            return buf.value
    except Exception:
        pass
    # Fallback
    return os.path.join(os.path.expanduser("~"), "Desktop")


def load_existing_entries(filepath):
    """Return set of (network, password) already stored, to avoid duplicates."""
    seen = set()
    if not os.path.isfile(filepath):
        return seen
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        for m in re.finditer(r"Network\s*:\s*(.+?)\s*\nPassword\s*:\s*(.+)", text):
            seen.add((m.group(1).strip(), m.group(2).strip()))
    except Exception:
        pass
    return seen


def main():
    if os.name != "nt":
        print("This script only works on Windows.")
        sys.exit(1)

    profiles = get_wifi_profiles()
    if not profiles:
        print("No Wi-Fi profiles found.")
        return

    out_file = os.path.join(get_desktop_path(), "Wi-Fi-Password.txt")
    already_seen = load_existing_entries(out_file)

    new_entries = []
    for profile in profiles:
        pwd = get_wifi_password(profile)
        if not pwd:
            continue
        if (profile, pwd) in already_seen:
            continue
        new_entries.append((profile, pwd))

    if not new_entries:
        print("[i] Nothing new to append — file already up to date.")
        print(f"[i] File: {out_file}")
        return

    # --- Append mode: "a" keeps previous content ---
    file_existed = os.path.isfile(out_file)
    with open(out_file, "a", encoding="utf-8") as f:
        if not file_existed:
            f.write("Wi-Fi Passwords (recovered from saved profiles)\n")
            f.write("=" * 50 + "\n\n")
        f.write(f"\n=== Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        for net, pwd in new_entries:
            f.write(f"Network : {net}\n")
            f.write(f"Password: {pwd}\n")
            f.write("-" * 40 + "\n")

    print(f"[+] Appended {len(new_entries)} new password(s).")
    print(f"[+] File: {out_file}")


if __name__ == "__main__":
    main()