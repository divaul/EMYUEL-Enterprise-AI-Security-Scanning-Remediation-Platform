"""GUI tabs package - Import all tab setup functions"""

from .ai_analysis_tab import setup_ai_analysis_tab
from .api_keys_tab import setup_api_tab
from .results_tab import setup_results_tab

__all__ = [
    'setup_ai_analysis_tab',
    'setup_api_tab',
    'setup_results_tab',
]
