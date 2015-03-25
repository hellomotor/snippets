import struct 
import sys

def main(argv):
    fs = open(argv[1], 'rb').read()
    off = 0
    version = struct.unpack_from('<i', fs, off)[0]
    print 'Length: %d Version: %d' % (len(fs), version)
    if version != 1000:
        sys.stderr.write('init file read failure, incorrect version\n')
        return
    off += struct.calcsize('<i')
    bourse = struct.unpack_from('<6272c', fs, off)
    off += struct.calcsize('<6272c')
    total = struct.unpack_from('<i', fs, off)[0]
    off += struct.calcsize('<i')
    fmt = '<lh6s16s16slL'
    fmt_size = struct.calcsize(fmt)
    print 'Total: %d, sizeof: %d' % (int(total), fmt_size)
    for i in xrange(int(total)):
        (_, ct, code, name, py, lastclose, vol5d) = struct.unpack_from(fmt, fs, off)
        print '0x%X\t%s\t%s' % (ct, code, name)
        off += fmt_size


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: %s initfile' % (sys.argv[0])
        sys.exit(1)
    main(sys.argv)
