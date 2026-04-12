from datetime import datetime
import importlib.metadata

try:
    __version__ = importlib.metadata.version("swapping_ebuilds")
except importlib.metadata.PackageNotFoundError:
    __version__ = 'NotFound'

__versiondatetime__ = datetime(2026, 4, 12, 8, 38)
__versiondate__ = __versiondatetime__.date()