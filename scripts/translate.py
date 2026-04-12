# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "swapping-ebuilds>=0.6.0",
# ]
# ///
import glob
from subprocess import run
py_files =  glob.glob("swapping_ebuilds/*.py")
run(["xgettext", "-L", "Python", "--no-wrap", "--no-location", "--from-code=UTF-8", "-o", "swapping_ebuilds/locale/swapping_ebuilds.pot"] + py_files, shell=False)
run(["msgmerge", "-N", "--no-wrap", "-U", "swapping_ebuilds/locale/es.po", "swapping_ebuilds/locale/swapping_ebuilds.pot"], shell=False)
run(["msgmerge", "-N", "--no-wrap", "-U", "swapping_ebuilds/locale/fr.po", "swapping_ebuilds/locale/swapping_ebuilds.pot"], shell=False)
run(["msgfmt", "-cv", "-o", "swapping_ebuilds/locale/es/LC_MESSAGES/swapping_ebuilds.mo", "swapping_ebuilds/locale/es.po"], shell=False)
run(["msgfmt", "-cv", "-o", "swapping_ebuilds/locale/fr/LC_MESSAGES/swapping_ebuilds.mo", "swapping_ebuilds/locale/fr.po"], shell=False)
