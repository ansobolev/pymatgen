#!/usr/bin/env python

from __future__ import division

'''
Created on Nov 8, 2011
'''

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Aug 12, 2012"

import argparse
from collections import OrderedDict

from pymatgen.io.vaspio import Vasprun
from pymatgen.electronic_structure.plotter import DosPlotter

parser = argparse.ArgumentParser(description='''
Convenient DOS Plotter for vasp runs.''', epilog="""
Author: {}
Version: {}
Last updated: {}""".format(__author__, __version__, __date__))

parser.add_argument('filename', metavar='filename', type=str, nargs=1,
                    help='vasprun.xml file to plot')

parser.add_argument('-s', '--site', dest='site', action='store_const',
                    const=True, help='plot site projected DOS')

parser.add_argument('-e', '--element', dest='element', type=str, nargs=1,
                    help='List of elements to plot as comma-separated ' + \
                    'values e.g., Fe,Mn')

parser.add_argument('-o', '--orbital', dest="orbital", action='store_const',
                    const=True, help='plot orbital projected DOS')

args = parser.parse_args()
v = Vasprun(args.filename[0])
dos = v.complete_dos

all_dos = OrderedDict()
all_dos['Total'] = dos

structure = v.final_structure

if args.site:
    for i in xrange(len(structure)):
        site = structure[i]
        all_dos['Site ' + str(i) + " " + site.specie.symbol] = \
            dos.get_site_dos(site)

if args.element:
    syms = [tok.strip() for tok in args.element[0].split(",")]
    el_dos = dos.get_element_dos()
    all_dos = {}
    for el, dos in dos.get_element_dos().items():
        if el.symbol in syms:
            all_dos[el] = dos
if args.orbital:
    all_dos = dos.get_spd_dos()

plotter = DosPlotter()
plotter.add_dos_dict(all_dos)
plotter.show()
