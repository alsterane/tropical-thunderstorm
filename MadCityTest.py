__author__ = 'Lars Herrmann'


from MadCityControl import *
import ctypes
import time

#MadCityControl.__init__()
controlStage = MadCityControl()

controlStage.initialise_stage()

print "x pos is " + str(controlStage.read_stage(1))
print "y pos is " + str(controlStage.read_stage(2))
controlStage.center_stage()

time.sleep(5)
print "x pos is " + str(controlStage.read_stage(1))
print "y pos is " + str(controlStage.read_stage(2))