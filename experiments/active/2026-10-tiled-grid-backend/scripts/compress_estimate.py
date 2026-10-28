# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Criterion A5: would block compression of the *canonical packed tiles* pay?

Parses TTK1 checkpoints (an independent reader of the format in DESIGN.md, including its FNV-1a checksum), compresses every
tile payload independently with deflate (zlib level 1 and 9) and xz (preset 0 and 6), and reports the total size against the packed
total. Each tile keeps its raw packed form when compression (plus a 4-byte header) would not make it smaller. Deflate and xz
compress at least as well as LZ4-class codecs, so a small gain here rules LZ4 out.

usage: uv run scripts/compress_estimate.py CKPT... > results/compress_estimate.json
"""
import json
import lzma
import struct
import sys
import zlib
from pathlib import Path


def fnv1a(b: bytes) -> int:
    h = 0xCBF29CE484222325
    for x in b:
        h = ((h ^ x) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def tiles(path: Path):
    b = path.read_bytes()
    assert b[:4] == b"TTK1", "bad magic"
    body, tail = b[:-8], b[-8:]
    assert fnv1a(body) == struct.unpack("<Q", tail)[0], "checksum"
    version, nl = struct.unpack_from("<II", body, 4)
    assert version == 1
    p = 12
    name = body[p : p + nl].decode()
    p += nl
    size, tl, w, steps, x, y, h, count = struct.unpack_from("<QIBQqqBQ", body, p)
    p += struct.calcsize("<QIBQqqBQ")
    out = []
    for _ in range(count):
        tx, ty, tag, ln = struct.unpack_from("<iiBI", body, p)
        p += 13
        out.append((tag, body[p : p + ln]))
        p += ln
    assert p == len(body)
    return dict(rule=name, board=size, tile_log2=tl, width=w, steps=steps, tiles=out)


def main() -> None:
    result = []
    for f in sys.argv[1:]:
        t = tiles(Path(f))
        payload = sum(len(d) for _, d in t["tiles"])
        row = dict(file=Path(f).name, rule=t["rule"], steps=t["steps"], colour_bits=t["width"], tiles=len(t["tiles"]), packed_total_bytes=payload)
        raw_dense = len(t["tiles"]) * (1 << t["tile_log2"]) ** 2
        row["raw_total_bytes"] = raw_dense
        for label, fn in [
            ("deflate1", lambda d: zlib.compress(d, 1)),
            ("deflate9", lambda d: zlib.compress(d, 9)),
            ("xz0", lambda d: lzma.compress(d, format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "preset": 0}])),
            ("xz6", lambda d: lzma.compress(d, format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "preset": 6}])),
        ]:
            total, used = 0, 0
            for _, d in t["tiles"]:
                c = fn(d)
                if len(c) + 4 < len(d):
                    total += len(c) + 4
                    used += 1
                else:
                    total += len(d)
            row[label] = dict(total_bytes=total, ratio_vs_packed=round(payload / total, 3), tiles_compressed=used)
        result.append(row)
    json.dump(result, sys.stdout, indent=1)
    print()


main()
