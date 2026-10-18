# -*- coding: utf-8 -*-
r"""Where the project drive is, found from this file's own location (KB §11 q22, §40).

The drive is Z: on the laptop and F: on the desktop. Every build script used to hard-code Z:, so
none of them ran on the desktop. They now build their paths with on_drive():

    from paths import on_drive, DRIVE
    GDB = on_drive(r"Mars Project\Mars Project.gdb")      # Z:\Mars Project\... or F:\Mars Project\...

DRIVE is two levels above build\ (build -> Mars Remote Sensing Project -> drive root), taken with
os.path.abspath, not resolve(), so a copy reached through a junction keeps its own root.

The no-space junctions Spatial Analyst needs (§19.1), <drive>\TypeArea, Global60 and Athabasca,
store an absolute target, so they work on one drive letter at a time (since §53.3 they point at F:,
so they are broken on Z:, §58). junction() checks and prints the fix; nothing here changes the file
system.
"""
import os

# join(..., "") adds exactly one trailing separator: "Z:\" stays "Z:\", a folder root gains one
DRIVE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "")
if os.environ.get("MARS_DRIVE"):              # override, e.g. for a test copy
    DRIVE = os.path.join(os.environ["MARS_DRIVE"], "")


def on_drive(rel=""):
    """<drive>\\<rel>. rel is written as it was under Z:\\, without the drive."""
    return os.path.join(DRIVE, rel) if rel else DRIVE


def junction(name):
    """<drive>\\<name>, the no-space alias of <drive>\\Mars Project\\<name>, checked to resolve here."""
    alias = on_drive(name)
    target = on_drive(os.path.join("Mars Project", name))
    if not os.path.isdir(alias):
        a = alias.rstrip("\\")
        if os.path.lexists(alias):            # e.g. retargeted on F:, seen from Z: (KB §58)
            raise SystemExit('broken junction %s (it targets another drive letter). Retarget it in place,\n'
                             'removing nothing (from build\\, either Python):\n'
                             '  py retarget_junction.py "%s" "%s"\n'
                             'The other machine then needs the same command with its own letter.'
                             % (alias, a, target))
        raise SystemExit('missing junction %s. Make it once (cmd, on this machine):\n  mklink /J "%s" "%s"'
                         % (alias, a, target))
    return alias


def arcgis_python():
    """The ArcGIS Pro Python. Pro is on C:\\Program Files on the laptop and on D:\\ArcGISPro on the
    desktop (KB §53.0), so read Pro's install folder from the registry; MARS_ARCGIS_PY overrides."""
    if os.environ.get("MARS_ARCGIS_PY"):
        return os.environ["MARS_ARCGIS_PY"]
    root = r"C:\Program Files\ArcGIS\Pro"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ESRI\ArcGISPro") as k:
            root = winreg.QueryValueEx(k, "InstallDir")[0]
    except OSError:
        pass
    return os.path.join(root, r"bin\Python\envs\arcgispro-py3\python.exe")


MARS_PROJECT = on_drive("Mars Project")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
APRX = on_drive(r"Mars Project\Mars Project.aprx")
BUILD = os.path.dirname(os.path.abspath(__file__))
