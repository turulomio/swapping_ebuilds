# Swapping ebuilds

## Links

* http://turulomio.users.sourceforge.net/doxygen/swapping_ebuilds/
* https://github.com/turulomio/swapping_ebuilds

## What is swapping_ebuilds?

It is a script designed to detect when compiling ebuilds in Gentoo Linux causes system swapping. With this tool, you can identify memory-hungry compilations on computers with limited RAM and optimize their compilation times.

Once you detect swapping ebuilds, you can change this behavior by using `/etc/portage/package.env` to reduce the number of parallel processes during compilation, which lowers the required RAM.

For example, if your `MAKEOPTS` in `/etc/portage/make.conf` uses `-j4`, and `dev-qt/qtwebengine` compilation is swapping, you can force it to use only `-j2` for this particular ebuild. First, create a file at `/etc/portage/env/makeopts-j2`:

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
swapping_ebuilds --get      # Run in the background to detect and log swapping
swapping_ebuilds --analyze  # Read the logs and view a swapping report
```

## Linux installation

You can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-admin/swapping_ebuilds
