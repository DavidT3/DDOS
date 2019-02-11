"""
This version (unlike the original) assumes that spectra have already been binned with required number of counts. Also
assumes the annular spectra are full circular annuli. Unlike original it applies the ARF (through the use of pyXSPEC).

ACTUALLY DOESN'T SEEM LIKE IT WILL WORK AS YOU CAN'T MODIFY SPECTRA IN THIS
"""

import sys
import os
from xspec import *
import pandas as pd
import numpy as np
from copy import deepcopy
from tqdm import trange


def read_conf_file(file_path):
    conf_info = pd.read_csv(file_path)
    return conf_info


def read_ang_spec(conf_row):
    og_dir = os.getcwd()
    annuli = np.empty((3, conf_row['num']), dtype=object)
    for j in range(0, conf_row['num']):
        if '/' in conf_row['prefix']:
            split_pref = conf_row['prefix'].split('/')
            directory = '/'.join(split_pref[0:-1])
            file_pref = split_pref[-1]
            os.chdir(directory)
        else:
            file_pref = conf_row['prefix']
        file_name = file_pref + str(j) + conf_row['suffix']
        # Stores Spectrum instance in numpy array (for df later)
        annuli[2, j] = Spectrum(file_name)
        # Stores annulus inner radius (uses the outer radius of last annulus, or input min radius for j=0)
        if j == 0:
            annuli[0, j] = float(conf_row['inrad'])
        elif j != 0:
            annuli[0, j] = annuli[1, j-1]
        # Stores annulus outer radius (grabs from fits XFLT0001 header)
        annuli[1, j] = annuli[2, j].fileinfo("XFLT0001")
        os.chdir(og_dir)

    headers = ["annulus{ident}".format(ident=el) for el in range(0, conf_row['num'])]
    annuli_df = pd.DataFrame(annuli, index=["inner radius", "outer radius", "og spectrum"], columns=headers)
    return annuli_df


def volume_project(shell_rad_inn, shell_rad_out, ann_rad_inn, ann_rad_out):
    """Return the projected volume of a shell of radius shell_rad_inn->shell_rad_out onto an
    annulus on the sky of ann_rad_inn->ann_rad_out.
    this is the integral:
    Int(y=ann_rad_inn,ann_rad_out) Int(x=sqrt(shell_rad_inn^2-y^2),sqrt(shell_rad_out^2-y^2)) 2*pi*y dx dy
     =
    Int(y=ann_rad_inn,ann_rad_out) 2*pi*y*( sqrt(shell_rad_out^2-y^2) - sqrt(shell_rad_inn^2-y^2) ) dy
    This is half the total volume (front only)
    """

    # If shell is lower radius than annulus it isn't going to contribute to emission.
    def trunc_sqrt(x):
        if x > 0:
            return np.sqrt(x)
        else:
            return 0.

    p1 = trunc_sqrt(shell_rad_inn ** 2 - ann_rad_out ** 2)
    p2 = trunc_sqrt(shell_rad_inn ** 2 - ann_rad_inn ** 2)
    p3 = trunc_sqrt(shell_rad_out ** 2 - ann_rad_out ** 2)
    p4 = trunc_sqrt(shell_rad_out ** 2 - ann_rad_inn ** 2)

    return (2./3.) * np.pi * ((p1**3 - p2**3) + (p4**3 - p3**3))


def randomise_spectra(annuli_df, num_random):
    Plot.device = "/xs"
    Plot.xAxis = "keV"

    for annulus in annuli_df:
        print("\n\nRandomising {ann}".format(ann=annulus))
        og_values = annuli_df[annulus]["og spectrum"].values
        og_variances = annuli_df[annulus]["og spectrum"].variance
        for j in trange(num_random):
            #annuli_df[annulus]["og spectrum"].__dict__['_Spectrum__values'] = np.random.normal(og_values, np.sqrt(og_variances))
            annuli_df[annulus]["og spectrum"].__dict__['_Spectrum__values'] = np.random.uniform(0, 1, len(og_values))

            sys.exit()
    sys.exit()

    return annuli_df


if __name__ == "__main__":
    XspecSettings.allowNewAttributes = True

    args = sys.argv[1:]
    if len(args) > 1:
        print('Too many flags')
        sys.exit(1)
    elif len(args) < 1:
        print('Too few flags')
        sys.exit(1)

    path = args[0]
    config = read_conf_file(path)

    for i, row in config.iterrows():
        annuli_data = read_ang_spec(row)
        annuli_data = randomise_spectra(annuli_data, 6000)



