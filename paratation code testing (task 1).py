#!/usr/bin/env python3

import argparse
import os
import struct

SECTOR_SIZE = 512

def parse_mbr(mbr):
    """Return 4 partition entries from the MBR."""
    entries = []

    # 4 entries, each 16 bytes, starting at offset 446
    for i in range(4):
        start = 446 + (i * 16)
        part = mbr[start:start + 16]

        status, _, ptype, _, lba_start, sectors = struct.unpack("<B3sB3sII", part)

        is_empty = (ptype == 0 or sectors == 0)

        if is_empty:
            size_gb = 0
        else:
            size_gb = (sectors * SECTOR_SIZE) / (1024**3)

        entries.append({
            "index": i,
            "ptype": ptype,
            "boot": (status == 0x80),
            "lba": lba_start,
            "sectors": sectors,
            "size_gb": size_gb,
            "empty": is_empty
        })

    return entries


def type_name(ptype):
    types = {
        0x07: "NTFS",
        0x0B: "FAT32",
        0x0C: "FAT32 LBA",
        0x0E: "FAT16 LBA",
        0x83: "Linux",
        0x82: "Linux Swap",
        0xEE: "GPT Protective"
    }
    return types.get(ptype, f"Unknown (0x{ptype:02X})")


def analyze(path):
    if not os.path.isfile(path):
        print("Image not found.")
        return

    with open(path, "rb") as f:
        mbr = f.read(SECTOR_SIZE)

    print(f"Opened image: {path}\n")

    parts = parse_mbr(mbr)

    print("--- MBR Partition Entries (Raw) ---")
    for i, p in enumerate(parts):
        print(f"Entry {i}: type=0x{p['ptype']:02X}, lba={p['lba']}, sectors={p['sectors']}")
    print("----------------------------------\n")

    print("=== Partition Table Analysis ===")
    real_parts = []

    # Print all 4 entries (including empty)
    for i, p in enumerate(parts, start=1):
        print(f"\nPartition #{i}")
        print(f"  Type        : 0x{p['ptype']:02X}")
        print(f"  Start LBA   : {p['lba']}")
        print(f"  Sectors     : {p['sectors']}")

        if p["empty"]:
            print("  Status      : Empty / Corrupt")
            print("  Size (GB)   : 0.00")
        else:
            print(f"  Status      : {'Bootable' if p['boot'] else 'Normal'}")
            print(f"  Type Name   : {type_name(p['ptype'])}")
            print(f"  Size (GB)   : {p['size_gb']:.2f}")
            real_parts.append(p)

    # Second real partition highlight
    print("\n=== Second Real Partition ===")
    if len(real_parts) >= 2:
        p = real_parts[1]
        print(f"  MBR Index   : {p['index']}")
        print(f"  Type        : {type_name(p['ptype'])}")
        print(f"  Start LBA   : {p['lba']}")
        print(f"  Size (GB)   : {p['size_gb']:.2f}")
    else:
        print("  Only one real partition found.")

    # Summary
    if real_parts:
        biggest = max(real_parts, key=lambda x: x["size_gb"])
        print("\n=== Summary ===")
        print(f"  Real partitions: {len(real_parts)}")
        print(f"  Largest type   : {type_name(biggest['ptype'])} ({biggest['size_gb']:.2f} GB)")


def main():
    parser = argparse.ArgumentParser(description="Simple MBR partition parser.")
    parser.add_argument("-i", "--image", help="Path to disk image (.dd)")
    args = parser.parse_args()

    if args.image:
        analyze(args.image)
    else:
        path = input("Enter path to .dd image: ")
        analyze(path)


if __name__ == "__main__":
    main()

