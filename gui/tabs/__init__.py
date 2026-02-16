"""
GUI Tabs Package
All modular tab setup functions
"""

from .quick_scan_tab import setup_quick_scan_tab
from .advanced_scan_tab import setup_advanced_tab
from .ai_analysis_tab import setup_ai_analysis_tab
from .api_keys_tab import setup_api_tab
from .reports_tab import setup_reports_tab  # Changed from results_tab

__all__ = [
    'setup_quick_scan_tab',
    'setup_advanced_tab',
    'setup_ai_analysis_tab',
    'setup_api_tab',
    'setup_reports_tab'  # Changed from setup_results_tab
]
