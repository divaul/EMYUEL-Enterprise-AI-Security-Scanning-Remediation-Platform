"""Color scheme for EMYUEL GUI - Premium cyber security theme"""

def get_color_scheme():
    """
    Get the premium cyber security color scheme
    
    Returns:
        dict: Color scheme with all theme colors
    """
    return {
        'bg_primary': '#0f1117',      # Darker main background
        'bg_secondary': '#1a1d29',    # Secondary background  
        'bg_tertiary': '#252836',     # Tertiary background (inputs, cards)
        'bg_hover': '#2d3142',        # Hover states
        'text_primary': '#e4e4e7',    # Primary text
        'text_secondary': '#a1a1aa',  # Secondary text (hints, labels)
        'text_tertiary': '#6b7280',   # Very muted text
        'accent_cyan': '#06b6d4',     # Cyan accent (primary actions)
        'accent_purple': '#a855f7',   # Purple accent (secondary)
        'accent_pink': '#ec4899',     # Pink accent (tertiary)
        'accent_gold': '#fbbf24',     # Gold accent (premium/warning)
        'success': '#10b981',         # Green (success states)
        'warning': '#f59e0b',         # Orange (warnings)
        'error': '#ef4444',           # Red (errors)
        'critical': '#dc2626',        # Dark red (critical issues)
        'info': '#38bdf8',            # Light blue (info)
        'border': '#374151',          # Border color
        'shadow': '#000000',          # Shadow color
    }
