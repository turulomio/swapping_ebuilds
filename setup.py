from setuptools import setup, Command
import datetime
import gettext
import os
from platform import system as platform_system
import site

gettext.install('swapping_ebuilds', 'swapping_ebuilds/locale')

class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.system("rm -Rf build")
        os.chdir("doc")
        os.system("doxygen Doxyfile") 

        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/swapping_ebuilds/ --delete-after")
        os.chdir("..")

class Procedure(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(_("New Release:"))
        print(_("  * Change version and date in version.py"))
        print(_("  * Edit Changelog in README"))
        print("  * python setup.py doc")
        print("  * mcedit locale/es.po")
        print("  * python setup.py doc")
        print("  * python setup.py install")
        print("  * python setup.py doxygen")
        print("  * git commit -a -m 'swapping_ebuilds-{}'".format(__version__))
        print("  * git push")
        print(_("  * Make a new tag in github"))
        print("  * python setup.py sdist upload -r pypi")
        print("  * python setup.py uninstall")
        print(_("  * Create a new gentoo ebuild with the new version"))
        print(_("  * Upload to portage repository")) 

class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform_system()=="Linux":
            os.system("rm -Rf {}/swapping_ebuilds*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/swapping_ebuilds")
        else:
            print(_("Uninstall command only works in Linux"))

class Doc(Command):
    description = "Update man pages and translations"
    user_options = [  ]
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #es
        os.system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/swapping_ebuilds.pot *.py swapping_ebuilds/*.py")
        os.system("msgmerge -N --no-wrap -U locale/es.po locale/swapping_ebuilds.pot")
        os.system("msgmerge -N --no-wrap -U locale/fr.po locale/swapping_ebuilds.pot")
        os.system("msgfmt -cv -o swapping_ebuilds/locale/es/LC_MESSAGES/swapping_ebuilds.mo locale/es.po")
        os.system("msgfmt -cv -o swapping_ebuilds/locale/fr/LC_MESSAGES/swapping_ebuilds.mo locale/fr.po")

class Reusing(Command):
    description = "Fetch remote modules"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sys import path
        path.append("swapping_ebuilds")
        from github import download_from_github
        download_from_github('turulomio','reusingcode','python/decorators.py', 'swapping_ebuilds')

## Version of modele captured from version to avoid problems with package dependencies
__version__= None
with open('swapping_ebuilds/__init__.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]

setup(name='swapping_ebuilds',
    version=__version__,
    description='Script to detect swapping compiling ebuilds in Gentoo',
    long_description="Project web page is in https://github.com/turulomio/swapping_ebuilds",
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: System Administrators',
                 'Topic :: System :: Systems Administration',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Programming Language :: Python :: 3',
                ],
    keywords='swap ebuild gentoo portage',
    url='https://github.com/turulomio/swapping_ebuilds',
    author='turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['swapping_ebuilds'],
    entry_points = {'console_scripts': ['swapping_ebuilds=swapping_ebuilds.main:main',
                                       ],
                   },
    install_requires=['humanize', 'psutil'],
    data_files=[],
    cmdclass={ 'doxygen': Doxygen,
               'doc': Doc,
               'uninstall': Uninstall,
               'procedure': Procedure,
               'reusing': Reusing,
             },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
