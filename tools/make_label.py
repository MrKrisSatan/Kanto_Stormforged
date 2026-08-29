#!/usr/bin/env python3
"""Generate KANTO: STORMFORGED cartridge label art using only stdlib."""
from pathlib import Path
import struct, zlib, sys

W = H = 512
buf = bytearray(W * H * 3)

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i+3] = bytes(c)

def rect(x0, y0, x1, y1, c):
    for y in range(max(0,y0), min(H,y1)):
        for x in range(max(0,x0), min(W,x1)):
            put(x,y,c)

def line(x0,y0,x1,y1,c,w=1):
    dx=abs(x1-x0); sx=1 if x0<x1 else -1
    dy=-abs(y1-y0); sy=1 if y0<y1 else -1
    err=dx+dy
    while True:
        for oy in range(-(w//2), w//2+1):
            for ox in range(-(w//2), w//2+1): put(x0+ox,y0+oy,c)
        if x0==x1 and y0==y1: break
        e2=2*err
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy

def poly(points,c):
    ymin=max(0,min(y for _,y in points)); ymax=min(H-1,max(y for _,y in points))
    for y in range(ymin,ymax+1):
        xs=[]
        for i,(x1,y1) in enumerate(points):
            x2,y2=points[(i+1)%len(points)]
            if y1==y2: continue
            if min(y1,y2) <= y < max(y1,y2):
                xs.append(int(x1+(y-y1)*(x2-x1)/(y2-y1)))
        xs.sort()
        for a,b in zip(xs[0::2], xs[1::2]):
            for x in range(max(0,a), min(W,b+1)): put(x,y,c)

FONT={
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01111","10000","10000","10000","10000","10000","01111"],
'D':["11110","10001","10001","10001","10001","10001","11110"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01111","10000","10000","10111","10001","10001","01111"],
'I':["11111","00100","00100","00100","00100","00100","11111"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","11001","10101","10011","10001","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","11011","10001"],
'Y':["10001","10001","01010","00100","00100","00100","00100"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00010","00100","01000","11111"],
'0':["01110","10001","10011","10101","11001","10001","01110"],
':':["00000","00100","00100","00000","00100","00100","00000"],
'-':["00000","00000","00000","11111","00000","00000","00000"],
' ':["00000"]*7,
}

def text(s,x,y,scale,c,spacing=1):
    start=x
    for ch in s.upper():
        glyph=FONT.get(ch,FONT[' '])
        for gy,row in enumerate(glyph):
            for gx,v in enumerate(row):
                if v=='1': rect(x+gx*scale,y+gy*scale,x+(gx+1)*scale,y+(gy+1)*scale,c)
        x += (5+spacing)*scale
    return x-start

# sky gradient
for y in range(H):
    t=y/(H-1)
    c=(int(17+14*t), int(25+39*t), int(36+42*t))
    rect(0,y,W,y+1,c)

# scanline / grid texture
for y in range(0,H,8): line(0,y,W-1,y,(13,22,31))
for x in range(0,W,32): line(x,0,x,H-1,(25,43,53))

# weather streaks
for x,y in [(40,84),(78,62),(118,106),(158,74),(196,120),(58,150),(140,160)]:
    line(x,y,x-9,y+19,(98,177,202),4)
for x,y in [(42,205),(86,197),(130,224),(178,202)]:
    line(x-8,y,x+8,y,(207,235,235),3); line(x,y-8,x,y+8,(207,235,235),3)

# lightning
poly([(290,42),(246,139),(279,139),(233,232),(331,115),(294,115),(334,42)],(246,220,111))

# autonomous-rival eye
rect(365,58,458,62,(116,239,221)); rect(365,144,458,148,(116,239,221))
rect(365,58,369,148,(116,239,221)); rect(454,58,458,148,(116,239,221))
for r in range(22,17,-1):
    # simple ring
    for a in range(360):
        import math
        x=411+int(math.cos(math.radians(a))*r); y=103+int(math.sin(math.radians(a))*r)
        put(x,y,(116,239,221))
rect(406,98,417,109,(244,235,144))
line(458,103,489,103,(116,239,221),4); line(365,103,334,103,(116,239,221),4)

# terrain silhouette
poly([(0,386),(52,354),(92,360),(128,328),(169,345),(216,307),(260,333),(308,296),(348,320),(399,283),(438,315),(476,295),(512,320),(512,512),(0,512)],(11,22,27))
line(0,386,52,354,(79,161,163),3); line(52,354,92,360,(79,161,163),3); line(92,360,128,328,(79,161,163),3)
line(128,328,169,345,(79,161,163),3); line(169,345,216,307,(79,161,163),3); line(216,307,260,333,(79,161,163),3)
line(260,333,308,296,(79,161,163),3); line(308,296,348,320,(79,161,163),3); line(348,320,399,283,(79,161,163),3)
line(399,283,438,315,(79,161,163),3); line(438,315,476,295,(79,161,163),3); line(476,295,511,320,(79,161,163),3)

# title plate
rect(24,246,488,386,(9,17,23))
line(24,246,488,246,(79,161,163),3); line(24,385,488,385,(79,161,163),3)
line(24,246,24,386,(79,161,163),3); line(487,246,487,386,(79,161,163),3)
text('KANTO',42,260,12,(241,239,218))
text('STORMFORGED',42,335,6,(116,239,221))
text('GEN1RECOMP CUSTOM CART',31,22,3,(183,218,219))
text('YELLOW - 12 MOD CART',166,417,3,(241,239,218))
text('WEATHER - VOXEL - ULTRON',166,451,2,(159,201,202))
text('MRKRISSATAN - 2026',166,476,2,(159,201,202))

# generic capture-disc emblem
for y in range(402,492):
    for x in range(52,142):
        dx=x-97; dy=y-447
        if dx*dx+dy*dy <= 45*45:
            put(x,y,(181,58,65) if y<447 else (231,232,222))
line(55,447,139,447,(9,17,21),7)
for y in range(433,461):
    for x in range(83,111):
        dx=x-97; dy=y-447
        if dx*dx+dy*dy <= 14*14: put(x,y,(239,235,211))

# PNG encode
raw=bytearray()
for y in range(H):
    raw.append(0); raw.extend(buf[y*W*3:(y+1)*W*3])
def chunk(tag,data):
    return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')
out=Path(sys.argv[1] if len(sys.argv)>1 else 'label.png')
out.write_bytes(png)
print(f'wrote {out} ({len(png)} bytes)')
