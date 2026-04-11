
from swapping_ebuilds import __version__


print("New Release:")
print("  * Change version and date in __init__.py")
print("  * Edit Changelog in README")
print("  * python tasks.py doc")
print("  * mcedit locale/es.po")
print("  * python tasks.py doc")
print("  * uv pip install .")
print("  * python tasks.py doxygen")
print(f"  * git commit -a -m 'swapping_ebuilds-{__version__}'")
print("  * git push")
print("  * Make a new tag in github")
print("  * uv build && uv publish")
print("  * python tasks.py uninstall")
print("  * Create a new gentoo ebuild with the new version")
print("  * Upload to portage repository") 

