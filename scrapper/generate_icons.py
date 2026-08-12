import os

def create_icon(size, filename):
    # PPM format is a very simple text-based image format that requires no libraries
    # Header: P3 (format), width, height, max_color_val
    header = f"P3\n{size} {size}\n255\n"
    
    # Body: Blue pixel data
    # We'll make a blue square with a slightly lighter center
    pixels = []
    for y in range(size):
        for x in range(size):
            # Border
            if x < 10 or x > size-10 or y < 10 or y > size-10:
                pixels.append("59 130 246") # Blue border (Tailwind-ish blue-500)
            else:
                pixels.append("30 41 59") # Dark slate fill
    
    body = "\n".join(pixels)
    
    # Save as .ppm
    ppm_path = filename + ".ppm"
    with open(ppm_path, "w") as f:
        f.write(header + body)
        
    print(f"Created {ppm_path}")
    
    # Use generic system tool to likely convert? 
    # Actually, simpler: Let's just assume we might not have PIL.
    # PPM is not supported by browsers usually.
    # Let's try to write a BMP manually. It's binary but simple header.
    
def create_bmp(size, filename):
    import struct
    
    width = size
    height = size
    
    # BMP Header
    # Magic (2), FileSize (4), Reserved (4), Offset (4)
    # InfoHeader: Size (4), W (4), H (4), Planes (2), Bits (2), Compress (4), IMGSize (4), ...
    
    file_size = 54 + 3 * width * height # 54 header + 3 bytes per pixel
    
    # Little-endian
    bmp_header = b'BM' + \
                 struct.pack('<I', file_size) + \
                 b'\x00\x00\x00\x00' + \
                 b'\x36\x00\x00\x00' # Offset 54
                 
    # DIB Header (BITMAPINFOHEADER)
    dib_header = struct.pack('<I', 40) + \
                 struct.pack('<i', width) + \
                 struct.pack('<i', height) + \
                 struct.pack('<H', 1) + \
                 struct.pack('<H', 24) + \
                 struct.pack('<I', 0) + \
                 struct.pack('<I', 3 * width * height) + \
                 struct.pack('<i', 0) + \
                 struct.pack('<i', 0) + \
                 struct.pack('<I', 0) + \
                 struct.pack('<I', 0)
                 
    # Pixel Data (BGR format, bottom-up)
    # Blue: 0x3B82F6 -> BGR: F6 82 3B
    # Dark: 0x1E293B -> BGR: 3B 29 1E
    
    pixels = bytearray()
    padding = (4 - (width * 3) % 4) % 4
    
    for y in range(height):
        row = bytearray()
        for x in range(width):
            if x < size//10 or x > size - size//10 or y < size//10 or y > size - size//10:
                row.extend(b'\xF6\x82\x3B') 
            else:
                 row.extend(b'\x3B\x29\x1E')
        row.extend(b'\x00' * padding)
        pixels.extend(row)
        
    with open(filename, 'wb') as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(pixels)
        
    print(f"Created {filename}")

os.makedirs("static/icons", exist_ok=True)
# We will create PNG if we can use an SVG and convert? No, that relies on external tools.
# Let's create BMPs but rename them to PNG? No, browser won't like that.
# Browsers support valid BMPs in manifest? Chrome might.
# Actually, SVG is text based!
# WE SHOULD CREATE SVGs!

def create_svg(size, filename):
    svg = f'''<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{size}" height="{size}" fill="#0f172a"/>
    <rect x="{size//4}" y="{size//4}" width="{size//2}" height="{size//2}" fill="#3b82f6" rx="{size//8}"/>
    <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="{size//3}" fill="white" font-weight="bold">CC</text>
</svg>'''
    
    with open(filename, "w") as f:
        f.write(svg)
    print(f"Created {filename}")

# Create SVGs as they are robustly supported and text-based
create_svg(192, "static/icons/icon-192x192.svg") # Using SVG instead of PNG for simplicity and quality
create_svg(512, "static/icons/icon-512x512.svg")

# Also create a PNG using the BMP trick for "apple-touch-icon" if strict png required? 
# Actually, modern browsers support SVG in manifest.
# But for broad compatibility (and if manifest requires type: image/png), we might need real PNGs.
# However, for this environment, SVG is the safest "pure code" generation.
# We will set type: "image/svg+xml" in manifest.
