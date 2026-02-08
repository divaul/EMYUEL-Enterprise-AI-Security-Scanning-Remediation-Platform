"""
Scanner Core - Main vulnerability scanning engine

REAL IMPLEMENTATION - imports from scanner-core directory
"""

import sys
from pathlib import Path

# Add scanner-core to path
current_dir = Path(__file__).parent
scanner_core_dir = current_dir / "scanner-core"

if scanner_core_dir.exists():
    sys.path.insert(0, str(scanner_core_dir))
    from scanner_core import ScannerCore
else:
    # Fallback if directory doesn't exist
    raise ImportError(
        f"Scanner core directory not found at {scanner_core_dir}. "
        "Please ensure scanner-core directory exists."
    )

__all__ = ['ScannerCore']
