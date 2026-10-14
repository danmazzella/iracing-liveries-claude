"""Decode an iRacing car_spec_<id>.mip (chunked zstd + BC3) to a PNG: python mipspec.py in.mip out.png (needs `pip install zstandard`)."""
import zstandard, struct, sys, io, re
from PIL import Image
def read_mip(path, want=2048):
    d=open(path,'rb').read(); Z=zstandard.ZstdDecompressor()
    for m in re.finditer(rb'DHMB',d):
        o=m.start(); w=struct.unpack('<I',d[o+16:o+20])[0]
        if w!=want<<8: continue
        a=d.index(b'ATAD',o); p=a+12
        cnt=struct.unpack('<I',d[p:p+4])[0]; q=p+12; out=b''
        for _ in range(cnt):
            sz=struct.unpack('<I',d[q:q+4])[0]; q+=4
            out+=Z.decompressobj().decompress(d[q:q+sz]); q+=sz
        return out
def bc3(raw,w):
    h=bytearray(128); h[0:4]=b'DDS '; struct.pack_into('<7I',h,4,124,0x81007,w,w,w*w,0,0)
    struct.pack_into('<II',h,76,32,4); h[84:88]=b'DXT5'
    struct.pack_into('<I',h,108,0x1000)
    return Image.open(io.BytesIO(bytes(h)+raw)).convert('RGBA')
if __name__=='__main__':
    raw=read_mip(sys.argv[1]); print(len(raw))
    bc3(raw,2048).save(sys.argv[2])
