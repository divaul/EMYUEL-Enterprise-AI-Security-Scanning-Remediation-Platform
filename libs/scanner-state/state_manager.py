"""
Scanner State Manager

Manages scanning state for pause/resume functionality.
Saves checkpoints periodically to allow resuming interrupted scans.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ScanStatus(Enum):
    """Scan status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScanProgress:
    """Scan progress tracking"""
    total_files: int = 0
    completed_files: int = 0
    current_file: Optional[str] = None
    current_detector: Optional[str] = None
    files_processed: List[str] = None
    
    def __post_init__(self):
        if self.files_processed is None:
            self.files_processed = []
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.completed_files / self.total_files) * 100


@dataclass
class ScanStateData:
    """Complete scan state"""
    scan_id: str
    target: str
    started_at: str
    status: str
    modules: List[str]
    progress: Dict[str, Any]
    findings: List[Dict[str, Any]]
    provider_state: Dict[str, Any]
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class StateManager:
    """
    Manages scan state for pause/resume
    
    Features:
    - Periodic checkpointing
    - Resume from exact position
    - State persistence to disk
    - Cleanup old states
    """
    
    def __init__(self, state_dir: Optional[Path] = None):
        """
        Initialize state manager
        
        Args:
            state_dir: Directory to store state files
                      (default: ~/.emyuel/state/)
        """
        if state_dir is None:
            state_dir = Path.home() / ".emyuel" / "state"
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_state: Optional[ScanStateData] = None
        self.checkpoint_interval = 10  # Save every N files
        
        logger.info(f"State manager initialized: {self.state_dir}")
    
    def init_scan(
        self,
        scan_id: str,
        target: str,
        modules: List[str],
        total_files: int
    ) -> ScanStateData:
        """
        Initialize new scan state
        
        Args:
            scan_id: Unique scan identifier
            target: Scan target (URL or path)
            modules: List of enabled detector modules
            total_files: Total number of files to scan
            
        Returns:
            Initialized scan state
        """
        self.current_state = ScanStateData(
            scan_id=scan_id,
            target=target,
            started_at=datetime.utcnow().isoformat(),
            status=ScanStatus.RUNNING.value,
            modules=modules,
            progress={
                'total_files': total_files,
                'completed_files': 0,
                'current_file': None,
                'current_detector': None,
                'files_processed': []
            },
            findings=[],
            provider_state={}
        )
        
        # Save initial state
        self.save_state()
        
        logger.info(f"Initialized scan state: {scan_id}")
        return self.current_state
    
    def update_progress(
        self,
        current_file: Optional[str] = None,
        current_detector: Optional[str] = None,
        completed_files: Optional[int] = None
    ):
        """Update scan progress"""
        if not self.current_state:
            return
        
        if current_file:
            self.current_state.progress['current_file'] = current_file
        
        if current_detector:
            self.current_state.progress['current_detector'] = current_detector
        
        if completed_files is not None:
            self.current_state.progress['completed_files'] = completed_files
        
        # Checkpoint periodically
        if completed_files and completed_files % self.checkpoint_interval == 0:
            self.save_state()
            logger.debug(f"Checkpoint saved at {completed_files} files")
    
    def mark_file_completed(self, filepath: str):
        """Mark file as completed"""
        if not self.current_state:
            return
        
        if filepath not in self.current_state.progress['files_processed']:
            self.current_state.progress['files_processed'].append(filepath)
            self.current_state.progress['completed_files'] = len(
                self.current_state.progress['files_processed']
            )
    
    def add_finding(self, finding: Dict[str, Any]):
        """Add vulnerability finding"""
        if not self.current_state:
            return
        
        self.current_state.findings.append(finding)
    
    def pause_scan(self):
        """Mark scan as paused"""
        if not self.current_state:
            return
        
        self.current_state.status = ScanStatus.PAUSED.value
        self.current_state.paused_at = datetime.utcnow().isoformat()
        self.save_state()
        
        logger.info(f"Scan paused: {self.current_state.scan_id}")
    
    def resume_scan(self):
        """Mark scan as resumed"""
        if not self.current_state:
            return
        
        self.current_state.status = ScanStatus.RUNNING.value
        self.current_state.paused_at = None
        self.save_state()
        
        logger.info(f"Scan resumed: {self.current_state.scan_id}")
    
    def complete_scan(self, error: Optional[str] = None):
        """Mark scan as completed or failed"""
        if not self.current_state:
            return
        
        if error:
            self.current_state.status = ScanStatus.FAILED.value
            self.current_state.error = error
        else:
            self.current_state.status = ScanStatus.COMPLETED.value
        
        self.current_state.completed_at = datetime.utcnow().isoformat()
        self.save_state()
        
        logger.info(f"Scan completed: {self.current_state.scan_id}")
    
    def cancel_scan(self):
        """Mark scan as cancelled"""
        if not self.current_state:
            return
        
        self.current_state.status = ScanStatus.CANCELLED.value
        self.current_state.completed_at = datetime.utcnow().isoformat()
        self.save_state()
        
        logger.info(f"Scan cancelled: {self.current_state.scan_id}")
    
    def save_state(self):
        """Save current state to disk"""
        if not self.current_state:
            return
        
        filepath = self.state_dir / f"{self.current_state.scan_id}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(self.current_state), f, indent=2)
            
            logger.debug(f"State saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")
    
    def load_state(self, scan_id: str) -> Optional[ScanStateData]:
        """
        Load scan state from disk
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            Loaded scan state or None if not found
        """
        filepath = self.state_dir / f"{scan_id}.json"
        
        if not filepath.exists():
            logger.warning(f"State file not found: {filepath}")
            return None
        
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            self.current_state = ScanStateData(**data)
            logger.info(f"State loaded: {scan_id}")
            return self.current_state
            
        except Exception as e:
            logger.error(f"Failed to load state: {str(e)}")
            return None
    
    def get_resumable_scans(self) -> List[Dict[str, Any]]:
        """
        Get list of scans that can be resumed
        
        Returns:
            List of resumable scan metadata
        """
        resumable = []
        
        for filepath in self.state_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                
                # Only include paused or failed scans
                if data.get('status') in [ScanStatus.PAUSED.value, ScanStatus.FAILED.value]:
                    resumable.append({
                        'scan_id': data['scan_id'],
                        'target': data['target'],
                        'status': data['status'],
                        'started_at': data['started_at'],
                        'paused_at': data.get('paused_at'),
                        'progress': data['progress']['completed_files'],
                        'total': data['progress']['total_files']
                    })
            except Exception as e:
                logger.error(f"Error reading state file {filepath}: {str(e)}")
        
        return sorted(resumable, key=lambda x: x['started_at'], reverse=True)
    
    def cleanup_old_states(self, days: int = 7):
        """
        Clean up old completed/cancelled states
        
        Args:
            days: Delete states older than this many days
        """
        from datetime import datetime, timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = 0
        
        for filepath in self.state_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                
                # Only delete completed/cancelled scans
                status = data.get('status')
                if status not in [ScanStatus.COMPLETED.value, ScanStatus.CANCELLED.value]:
                    continue
                
                # Check age
                completed_at = data.get('completed_at')
                if completed_at:
                    completed_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    if completed_time < cutoff:
                        filepath.unlink()
                        deleted += 1
                        logger.debug(f"Deleted old state: {filepath.name}")
            
            except Exception as e:
                logger.error(f"Error cleaning up {filepath}: {str(e)}")
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old state files")
    
    def get_progress(self) -> Optional[ScanProgress]:
        """Get current scan progress"""
        if not self.current_state:
            return None
        
        return ScanProgress(**self.current_state.progress)
    
    def is_file_processed(self, filepath: str) -> bool:
        """Check if file has already been processed"""
        if not self.current_state:
            return False
        
        return filepath in self.current_state.progress.get('files_processed', [])
