import pip
import pprint
# import RPi.GPIO as io

prettyPrint = pprint.PrettyPrinter(indent=2).pprint

# prettyPrint(io.__file__) # location of a module

installed_packages = pip.get_installed_distributions()

#installed_packages_sorted = sorted([i.key for i in installed_packages])

installed_packages_list = sorted(["%s  ==  %s" % (i.key, i.version) for i in installed_packages])

prettyPrint(installed_packages_list)
