
from swapping_ebuilds import __version__


print("New Release:")
print("  * Create an issue in Github and create associated branch")
print("  * Change version and date in __init__.py")
print("  * uv run -s scripts/release.py")
print("  * Edit Changelog in README")
print("  * uv run -s scripts/translate.py")
print("  * mcedit locale/es.po")
print("  * uv run -s scripts/translate.py")
print(f"  * git commit -a -m 'swapping_ebuilds-{__version__}'")
print("  * git push")
print("  * Make a new tag in github")
print("  * uv build && uv publish")
print("  * Create a new gentoo ebuild with the new version")
print("  * Upload to portage repository") 

