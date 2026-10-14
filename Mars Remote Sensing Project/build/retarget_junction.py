# -*- coding: utf-8 -*-
r"""Retarget an existing directory junction IN PLACE (FSCTL_SET_REPARSE_POINT), without removing it.

    py retarget_junction.py <junction> <new target>

Refuses unless <junction> is already a mount-point reparse point (a junction) and <new target> is an
existing directory. Prints the old and new targets.

Why (KB §53.3): the no-space junctions <drive>\TypeArea, Global60, Athabasca store an absolute target, so
the ones made on Z: are broken on F:. The handoff's fix is rmdir + mklink /J; an agent's shell may refuse
rmdir at a drive-root path. This changes the target in place and removes nothing:

    py retarget_junction.py "F:\TypeArea" "F:\Mars Project\TypeArea"

Stdlib only (ctypes); either Python; no admin rights needed for a junction.
"""
import ctypes, os, struct, sys
from ctypes import wintypes

FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
OPEN_EXISTING = 3
FSCTL_GET_REPARSE_POINT = 0x000900A8
FSCTL_SET_REPARSE_POINT = 0x000900A4
IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003
INVALID = ctypes.c_void_p(-1).value

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateFileW.restype = wintypes.HANDLE
k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
k32.DeviceIoControl.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                                ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]


def open_rp(path, access):
    h = k32.CreateFileW(path, access, 0x7, None, OPEN_EXISTING,
                        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS, None)
    if h == INVALID:
        raise ctypes.WinError(ctypes.get_last_error())
    return h


def get_target(path):
    h = open_rp(path, GENERIC_READ)
    try:
        buf = ctypes.create_string_buffer(16384); n = wintypes.DWORD()
        if not k32.DeviceIoControl(h, FSCTL_GET_REPARSE_POINT, None, 0, buf, len(buf), ctypes.byref(n), None):
            raise ctypes.WinError(ctypes.get_last_error())
        tag, _, _, so, sl, po, pl = struct.unpack_from("<IHHHHHH", buf.raw)
        if tag != IO_REPARSE_TAG_MOUNT_POINT:
            raise SystemExit("%s is not a junction (tag 0x%08X)" % (path, tag))
        pb = buf.raw[16:]
        return pb[so:so + sl].decode("utf-16-le"), pb[po:po + pl].decode("utf-16-le")
    finally:
        k32.CloseHandle(h)


def set_target(path, target):
    sub = ("\\??\\" + target).encode("utf-16-le"); prn = target.encode("utf-16-le")
    pathbuf = sub + b"\0\0" + prn + b"\0\0"
    data = struct.pack("<HHHH", 0, len(sub), len(sub) + 2, len(prn)) + pathbuf
    rp = struct.pack("<IHH", IO_REPARSE_TAG_MOUNT_POINT, len(data), 0) + data
    h = open_rp(path, GENERIC_WRITE)
    try:
        n = wintypes.DWORD()
        if not k32.DeviceIoControl(h, FSCTL_SET_REPARSE_POINT, rp, len(rp), None, 0, ctypes.byref(n), None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    j, t = sys.argv[1], os.path.abspath(sys.argv[2])
    if not os.path.isdir(t):
        raise SystemExit("target %s is not a directory" % t)
    old = get_target(j)
    print("old:", old)
    set_target(j, t)
    print("new:", get_target(j))
    print("resolves:", os.path.isdir(j), "| same folder as target:", os.path.samefile(j, t))
