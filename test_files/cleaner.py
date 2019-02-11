import sys
from astropy.io import fits


if __name__ == "__main__":
    arg = sys.argv[1]
    boi = fits.open(arg, mode='update')
    for el in boi['SPECTRUM'].header:
        val = str(boi['SPECTRUM'].header[el])
        if "/lustre" in val:
            print(el)
            trunc_val = val.split('/')[-1]
            boi['SPECTRUM'].header[el] = trunc_val

    boi.flush()





