# -*- coding: utf-8 -*-
r"""Where the project drive is, found from this file's own location (KB §11 q22, §40).

The drive is Z: on the laptop and F: on the desktop. Every build script used to hard-code Z:, so
none of them ran on the desktop. They now build their paths with on_drive():

    from paths import on_drive, DRIVE
    GDB = on_drive(r"Mars Project\Mars Project.gdb")      # Z:\Mars Project\... or F:\Mars Project\...

DRIVE is two levels above build\ (build -> Mars Remote Sensing Project -> drive root), taken with
os.path.abspath, not resolve(), so a copy reached through a junction keeps its own root.

The two no-space junctions Spatial Analyst needs (§19.1), <drive>\TypeArea and <drive>\Global60,
store an absolute target. Made on Z:, they point at Z:\... and are broken on F:. junction() checks
and says how to recreate one; nothing here changes the file system.
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
        stale = os.path.lexists(alias)        # e.g. made on Z:, still pointing at Z:\..., seen from F:
        raise SystemExit('%s junction %s. Fix it once (cmd, on this machine):\n%s'
                         '  mklink /J "%s" "%s"'
                         % ("broken" if stale else "missing", alias,
                            '  rmdir "%s"\n' % alias.rstrip("\\") if stale else "",
                            alias.rstrip("\\"), target))
    return alias


MARS_PROJECT = on_drive("Mars Project")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
APRX = on_drive(r"Mars Project\Mars Project.aprx")
BUILD = os.path.dirname(os.path.abspath(__file__))
