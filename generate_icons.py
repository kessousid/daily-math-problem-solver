"""Run this once to generate PWA icons: python generate_icons.py"""
import struct, zlib, math

def make_png(size):
    bg      = (13, 13, 31)
    purple1 = (139, 92, 246)
    purple2 = (67, 56, 202)
    gold1   = (253, 230, 138)
    gold2   = (245, 158, 11)

    pixels = []
    cx, cy = size / 2, size / 2
    r  = size / 2
    rr = r * 0.85   # inner radius for rounded square check

    def in_rounded_square(x, y, radius=0.215):
        nx = (x - cx) / r
        ny = (y - cy) / r
        rn = radius
        # superellipse approximation for rounded square
        val = abs(nx)**4 + abs(ny)**4
        return val <= (1 - rn)**4 * 1.6

    def lerp(a, b, t):
        return int(a + (b - a) * t)

    def lerp_color(c1, c2, t):
        return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

    # Lightning bolt polygon points (normalised 0-1)
    bolt_pts_norm = [(0.586, 0.133), (0.484, 0.426), (0.559, 0.426),
                     (0.453, 0.820), (0.766, 0.398), (0.680, 0.398), (0.773, 0.133)]
    bolt_pts = [(int(p[0] * size), int(p[1] * size)) for p in bolt_pts_norm]

    def point_in_polygon(px, py, poly):
        n = len(poly)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
                inside = not inside
            j = i
        return inside

    for y in range(size):
        row = []
        for x in range(size):
            if not in_rounded_square(x, y):
                row += [0, 0, 0, 0]
                continue

            # Background gradient: top-left purple to bottom-right indigo
            t = ((x + y) / (2 * size))
            r_val, g_val, b_val = lerp_color(purple1, purple2, t)

            # Lightning bolt
            if point_in_polygon(x, y, bolt_pts):
                bt = y / size
                rc, gc, bc = lerp_color(gold1, gold2, bt)
                row += [rc, gc, bc, 255]
            else:
                row += [r_val, g_val, b_val, 255]
        pixels.append(bytes(row))

    def make_chunk(tag, data):
        c = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', c)

    raw = b''.join(b'\x00' + row for row in pixels)
    compressed = zlib.compress(raw, 9)

    png = (
        b'\x89PNG\r\n\x1a\n'
        + make_chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
        + make_chunk(b'IDAT', compressed)
        + make_chunk(b'IEND', b'')
    )
    return png

for sz in [32, 192, 512]:
    data = make_png(sz)
    path = f'static/icon-{sz}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Created {path} ({len(data):,} bytes)')

print('Done!')
