"""Run this once to generate PWA icons: python generate_icons.py"""
import struct, zlib, math

def make_png(size, bg=(13, 13, 31), accent=(139, 92, 246)):
    """Generate a simple purple-gradient icon PNG with a lightning bolt."""
    pixels = []
    cx, cy = size // 2, size // 2
    r = size // 2

    # Lightning bolt path (simplified, pixel-based)
    bolt = set()
    scale = size / 100
    pts = [(55,10),(35,50),(50,50),(45,90),(65,45),(50,45),(55,10)]
    for i in range(len(pts)-1):
        x0,y0 = int(pts[i][0]*scale), int(pts[i][1]*scale)
        x1,y1 = int(pts[i+1][0]*scale), int(pts[i+1][1]*scale)
        steps = max(abs(x1-x0), abs(y1-y0), 1)
        for s in range(steps+1):
            bx = round(x0 + (x1-x0)*s/steps)
            by = round(y0 + (y1-y0)*s/steps)
            for dx in range(-max(1,size//40), max(2,size//35)):
                for dy in range(-max(1,size//40), max(2,size//35)):
                    bolt.add((bx+dx, by+dy))

    for y in range(size):
        row = []
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            # Circular mask
            if dist > r - 1:
                row += [0, 0, 0, 0]
                continue
            # Gradient background: deep purple
            t = dist / r
            pr = int(bg[0] + (accent[0]-bg[0]) * (1-t) * 0.4)
            pg = int(bg[1] + (accent[1]-bg[1]) * (1-t) * 0.4)
            pb = int(bg[2] + (accent[2]-bg[2]) * (1-t) * 0.6)
            # Lightning bolt
            if (x, y) in bolt:
                pr, pg, pb = 255, 230, 80  # yellow/gold bolt
            row += [pr, pg, pb, 255]
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

for sz in [192, 512]:
    data = make_png(sz)
    path = f'static/icon-{sz}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Created {path} ({len(data):,} bytes)')

print('Done! Icons saved to static/')
