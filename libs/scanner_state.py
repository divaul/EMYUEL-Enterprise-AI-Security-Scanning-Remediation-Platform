"""
Scanner State Manager - Pause/Resume functionality
"""

# Import from actual implementation in scanner-state directory
import sys
from pathlib import Path

# Add scanner-state to path
current_dir = Path(__file__).parent
state_dir = current_dir / "scanner-state"
if state_dir.exists():
    sys.path.insert(0, str(state_dir))

try:
    from state_manager import StateManager, ScanState
    __all__ = ['StateManager', 'ScanState']
except ImportError:
    # Fallback: create minimal implementation
    import json
    from pathlib import Path
    from datetime import datetime
    from typing import Optional, Dict, Any, List
    
    class ScanState:
        """Scan state data class"""
        def __init__(self, scan_id, target, status='running', **kwargs):
            self.scan_id = scan_id
            self.target = target
            self.status = status
            self.progress = kwargs.get('progress', {})
            self.findings = kwargs.get('findings', [])
            self.started_at = kwargs.get('started_at', datetime.now().isoformat())
            self.paused_at = kwargs.get('paused_at', None)
    
    class StateManager:
        """Minimal State Manager stub"""
        def __init__(self, states_dir=None):
            if states_dir is None:
                states_dir = Path.home() / ".emyuel" / "states"
            self.states_dir = Path(states_dir)
            self.states_dir.mkdir(parents=True, exist_ok=True)
        
        def save_state(self, state: ScanState):
            """Save scan state to disk"""
            state_file = self.states_dir / f"{state.scan_id}.json"
            state_data = {
                'scan_id': state.scan_id,
                'target': state.target,
                'status': state.status,
                'progress': state.progress,
                'findings': state.findings,
                'started_at': state.started_at,
                'paused_at': state.paused_at or datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        
        def load_state(self, scan_id: str) -> Optional[ScanState]:
            """Load scan state from disk"""
            state_file = self.states_dir / f"{scan_id}.json"
            if not state_file.exists():
                return None
            
            with open(state_file, 'r') as f:
                data = json.load(f)
            
            return ScanState(**data)
        
        def get_resumable_scans(self) -> List[Dict[str, Any]]:
            """Get list of resumable scans"""
            scans = []
            for state_file in self.states_dir.glob("*.json"):
                try:
                    with open(state_file, 'r') as f:
                        data = json.load(f)
                    
                    total = data.get('progress', {}).get('total_files', 0)
                    progress = data.get('progress', {}).get('completed_files', 0)
                    
                    scans.append({
                        'scan_id': data.get('scan_id'),
                        'target': data.get('target'),
                        'status': data.get('status'),
                        'progress': progress,
                        'total': total,
                        'started_at': data.get('started_at')
                    })
                except:
                    continue
            
            return scans
        
        def pause_scan(self):
            """Pause current scan"""
            pass
    
    __all__ = ['StateManager', 'ScanState']
