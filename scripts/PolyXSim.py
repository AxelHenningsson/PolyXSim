#!/usr/bin/env python

# Modules to import 
import sys
from polyxsim import check_input
from polyxsim import find_refl
from polyxsim import generate_grains
from polyxsim import make_image
from polyxsim import make_imagestack
from polyxsim import reflections
import logging
logging.basicConfig(level=logging.INFO,format='\n%(levelname)s: %(message)s')

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input", action="store",
                  dest="filename", type="string",
                  help="Name of the file containing the input parameters")
parser.add_option("-d", "--debug", action="store_true",
                  dest="debug",default =False,
                  help="Run in debug mode")
options , args = parser.parse_args()

if options.filename == None:
    parser.print_help()
    print "\nNo input file supplied [-i filename]\n"
    sys.exit()

print '\n'


# Is the input file available?

# Read and check input

# Make instance of parse_input class
logging.info('Reading input\n')

myinput = check_input.parse_input(input_file=options.filename)

myinput.read()                                # read input file
#except:
#    logging.error('Cannot read input - exit')
#sys.exit()

logging.info('Checking input\n')
myinput.check()                               # check validity of input


if myinput.missing == True:                   # if problem exit
    logging.info('MISSING ITEMS')
    sys.exit()

logging.info('Initialize parameters etc\n')
myinput.initialize()                            # if ok initialize

#print myinput.param
generate_grains.generate_grains(myinput.param)
generate_grains.save_grains(myinput.param)
generate_grains.save_ubi(myinput.param)

# Generate reflections
if 'structure_file' in myinput.param:
    xtal_structure = reflections.open_structure(myinput.param)
    logging.info('Generating miller indices')
    hkl = reflections.gen_miller(myinput.param)
    logging.info('Structure factor calculation')
    hkl = reflections.calc_intensity(hkl,xtal_structure)
else:
    hkl = reflections.gen_miller(myinput.param)
    hkl = reflections.add_intensity(hkl,myinput.param)




# Determine the reflection parameters for grains
graindata = find_refl.find_refl(myinput.param,hkl)
graindata.frameinfo = myinput.frameinfo
logging.info('Determine reflections positions')
graindata.run()
logging.info('Save reflections')
graindata.save()
logging.info('Write g-vector file')
graindata.write_gve()

if myinput.param['make_image'] == 1:
	image = make_image.make_image(graindata)
	image.make_image()
elif  myinput.param['make_image'] == 2:
	image = make_imagestack.make_image(graindata)
	image.setup_odf()
	image.make_image()
	image.correct_image()
    