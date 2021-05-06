# Swapping ebuilds

## What is swapping_ebuilds

It's a script to detect swapping compiling ebuilds in Gentoo. With this tool you can detect swapping in computers with small RAM to try to improve its compilation time.

Once you detect swapping ebuilds you can change this behaviour using, you can use /etc/portage/package.env to change the number of paralell process in compilation to reduce the needed RAM.

For example if your MAKEOPTS in /etc/portage/make.conf uses -j4, and dev-qt/qtwebengine compilation is swapping, you can force to use only -j2 with this particular ebuild,  creating a file in `/etc/portage/env/makeopts-j2`

```bash
MAKEOPTS="-j2"
```

and then edit `/etc/portage/package.env`
```
dev-qt/qtwebengine makeopts-j2
```

Next time you compile dev-qt/qtwebengine, Gentoo will use only 2 concurrent process

## Usage

```bash
swapping_ebuilds --get # To detect swapping
swapping_ebuilds --analyze # To see a swapping report
```

## Linux installation

You can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-admin/swapping_ebuilds

## Dependencies

* https://www.python.org/, as the main programming language.
* https://github.com/tartley/colorama
* https://github.com/jmoiron/humanize
* https://github.com/giampaolo/psutil

## Changelog

### 0.5.0 (2021-05-06)

* Added --list argument to list registers
* Added highlighted ouput with colorama

### 0.4.0 (2021-05-02)

* Changed system to swap variation instead of a limit of swap to log
* Added --clean parameter to clean log

### 0.3.0 (2021-02-21)

* Improved Logging output.
* Captured CTRL+C keys.

### 0.2.0 (2020-12-31)

* Script converted to a python package

### 0.1.0 (2020-12-13)

* Script migrated to this project from myportage repository
