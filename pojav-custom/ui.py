#!/usr/bin/env python3
"""Tiny uiautomator driver: ui.py tap-id <id> | tap-text <regex> | texts"""
import re, subprocess, sys, xml.etree.ElementTree as ET

def adb(*a):
    return subprocess.run(["adb", *a], capture_output=True, text=True).stdout

def nodes():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    xml = adb("exec-out", "cat", "/sdcard/ui.xml")
    try:
        root = ET.fromstring(xml[xml.index("<"):])
    except Exception:
        return []
    return list(root.iter("node"))

def center(n):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", n.get("bounds", ""))
    if not m:
        return None
    l, t, r, b = map(int, m.groups())
    return (l + r) // 2, (t + b) // 2

def tap(n):
    c = center(n)
    if c:
        adb("shell", "input", "tap", str(c[0]), str(c[1]))
        print(f"tapped {n.get('resource-id') or n.get('text')} at {c}")
        return True
    return False

cmd = sys.argv[1]
ns = nodes()
if cmd == "texts":
    for n in ns:
        t, i = n.get("text"), n.get("resource-id")
        if t or i:
            print(f"{i!s:60} | {t!s:40} | {n.get('bounds')}")
elif cmd == "tap-id":
    for n in ns:
        if (n.get("resource-id") or "").endswith(":id/" + sys.argv[2]) and tap(n):
            sys.exit(0)
    print("id not found:", sys.argv[2]); sys.exit(1)
elif cmd == "tap-text":
    rx = re.compile(sys.argv[2], re.I)
    for n in ns:
        if rx.search(n.get("text") or "") and tap(n):
            sys.exit(0)
    print("text not found:", sys.argv[2]); sys.exit(1)
