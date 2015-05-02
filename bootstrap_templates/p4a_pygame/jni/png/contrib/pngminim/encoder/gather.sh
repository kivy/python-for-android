cp ../../pngminus/pnm2png.c pnm2pngm.c
cp ../../../*.h .
cp ../../../*.c .
rm example.c pnggccrd.c pngvcrd.c pngtest.c pngr*.c pngpread.c
# Change the next 2 lines if zlib is somewhere else.
cp ../../../../zlib/*.h .
cp ../../../../zlib/*.c .
rm inf*.[ch]
rm minigzip.c example.c
