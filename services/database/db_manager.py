"""
Database Manager for EMYUEL Scan History
Uses SQLite for persistent storage of scans, findings, and reports
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager


class DatabaseManager:
    """Manage scan history database with SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
                    Default: ~/.emyuel/scan_history.db
        """
        if db_path is None:
            db_path = Path.home() / ".emyuel" / "scan_history.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with automatic commit/rollback"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema if not exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create scans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    target_url TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds REAL,
                    total_findings INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'completed',
                    critical_count INTEGER DEFAULT 0,
                    high_count INTEGER DEFAULT 0,
                    medium_count INTEGER DEFAULT 0,
                    low_count INTEGER DEFAULT 0,
                    info_count INTEGER DEFAULT 0,
                    modules_used TEXT,
                    total_pages_scanned INTEGER,
                    user_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create findings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    vulnerability_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT NOT NULL,
                    parameter TEXT,
                    method TEXT,
                    evidence TEXT,
                    request_data TEXT,
                    response_data TEXT,
                    remediation TEXT,
                    references TEXT,
                    cvss_score REAL,
                    cvss_vector TEXT,
                    owasp_category TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
                )
            """)
            
            # Create scan_modules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    findings_count INTEGER DEFAULT 0,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE,
                    UNIQUE(scan_id, module_name)
                )
            """)
            
            # Create reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    ai_provider TEXT,
                    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_target ON scans(target_url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_scan ON findings(scan_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity)")
    
    # ============ SCAN OPERATIONS ============
    
    def save_scan(self, scan_data: Dict[str, Any]) -> str:
        """
        Save scan results to database
        
        Args:
            scan_data: Dictionary containing scan results
                Required keys: scan_id, target, findings
                Optional: scan_type, modules, total_pages
        
        Returns:
            scan_id of saved scan
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Extract basic data
            scan_id = scan_data.get('scan_id', f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            target_url = scan_data.get('target', 'unknown')
            scan_type = scan_data.get('scan_type', 'quick')
            
            # Get findings
            findings = scan_data.get('findings', [])
            total_findings = len(findings)
            
            # Count by severity
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            for finding in findings:
                sev = finding.get('severity', 'info').lower()
                if sev in severity_counts:
                    severity_counts[sev] += 1
            
            # Prepare modules JSON
            modules_used = json.dumps(scan_data.get('modules', []))
            
            # Insert scan record
            cursor.execute("""
                INSERT INTO scans (
                    scan_id, target_url, scan_type, total_findings,
                    critical_count, high_count, medium_count, low_count, info_count,
                    modules_used, total_pages_scanned, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id, target_url, scan_type, total_findings,
                severity_counts['critical'], severity_counts['high'],
                severity_counts['medium'], severity_counts['low'], severity_counts['info'],
                modules_used, scan_data.get('total_pages', 0), 'completed'
            ))
            
            # Save each finding
            for finding in findings:
                self._save_finding(cursor, scan_id, finding)
            
            # Save modules
            for module in scan_data.get('modules', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO scan_modules (scan_id, module_name)
                    VALUES (?, ?)
                """, (scan_id, module))
            
            return scan_id
    
    def _save_finding(self, cursor, scan_id: str, finding: Dict[str, Any]):
        """Save individual finding to database"""
        cursor.execute("""
            INSERT INTO findings (
                scan_id, severity, vulnerability_type, title, description,
                url, parameter, method, evidence, remediation, references
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            finding.get('severity', 'info'),
            finding.get('type', 'Unknown'),
            finding.get('title', 'Vulnerability Found'),
            finding.get('description', ''),
            finding.get('url', ''),
            finding.get('parameter', ''),
            finding.get('method', 'GET'),
            finding.get('evidence', ''),
            finding.get('remediation', ''),
            json.dumps(finding.get('references', []))
        ))
    
    def get_all_scans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all scans ordered by timestamp (newest first)
        
        Args:
            limit: Maximum number of scans to return
        
        Returns:
            List of scan dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scans
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            scans = []
            for row in cursor.fetchall():
                scan = dict(row)
                # Parse JSON fields
                if scan.get('modules_used'):
                    try:
                        scan['modules'] = json.loads(scan['modules_used'])
                    except (json.JSONDecodeError, ValueError, TypeError):
                        scan['modules'] = []
                scans.append(scan)
            
            return scans
    
    def get_scan_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scan by ID with all findings
        
        Args:
            scan_id: Unique scan identifier
        
        Returns:
            Scan dictionary with findings, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get scan metadata
            cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
            scan_row = cursor.fetchone()
            
            if not scan_row:
                return None
            
            scan = dict(scan_row)
            
            # Parse modules JSON
            if scan.get('modules_used'):
                try:
                    scan['modules'] = json.loads(scan['modules_used'])
                except (json.JSONDecodeError, ValueError, TypeError):
                    scan['modules'] = []
            
            # Get findings
            cursor.execute("""
                SELECT * FROM findings
                WHERE scan_id = ?
                ORDER BY 
                    CASE severity
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    id ASC
            """, (scan_id,))
            
            findings = []
            for row in cursor.fetchall():
                finding = dict(row)
                # Parse references JSON
                if finding.get('references'):
                    try:
                        finding['references'] = json.loads(finding['references'])
                    except (json.JSONDecodeError, ValueError, TypeError):
                        finding['references'] = []
                findings.append(finding)
            
            scan['findings'] = findings
            
            return scan
    
    def delete_scan(self, scan_id: str) -> bool:
        """
        Delete scan and all related data
        
        Args:
            scan_id: Scan to delete
        
        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
            return cursor.rowcount > 0
    
    def search_scans(self, query: str) -> List[Dict[str, Any]]:
        """
        Search scans by target URL
        
        Args:
            query: Search string for target URL
        
        Returns:
            List of matching scans
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scans
                WHERE target_url LIKE ?
                ORDER BY timestamp DESC
            """, (f"%{query}%",))
            
            scans = []
            for row in cursor.fetchall():
                scan = dict(row)
                if scan.get('modules_used'):
                    try:
                        scan['modules'] = json.loads(scan['modules_used'])
                    except (json.JSONDecodeError, ValueError, TypeError):
                        scan['modules'] = []
                scans.append(scan)
            
            return scans
    
    def update_scan_status(self, scan_id: str, status: str):
        """
        Update scan status
        
        Args:
            scan_id: Scan to update
            status: New status ('completed', 'paused', 'failed')
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scans
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE scan_id = ?
            """, (status, scan_id))
    
    # ============ REPORT OPERATIONS ============
    
    def save_report(self, scan_id: str, report_type: str, file_path: str, **kwargs):
        """
        Save generated report record
        
        Args:
            scan_id: Associated scan
            report_type: Type of report ('ai_enhanced', 'raw_json', 'html', 'pdf', 'csv')
            file_path: Path to generated report file
            **kwargs: Optional: file_size, ai_provider
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (scan_id, report_type, file_path, file_size, ai_provider)
                VALUES (?, ?, ?, ?, ?)
            """, (
                scan_id, report_type, file_path,
                kwargs.get('file_size'), kwargs.get('ai_provider')
            ))
    
    def get_reports_for_scan(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get all reports for a scan
        
        Args:
            scan_id: Scan ID
        
        Returns:
            List of report dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reports
                WHERE scan_id = ?
                ORDER BY generated_at DESC
            """, (scan_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ============ STATISTICS ============
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """
        Get overall scan statistics
        
        Returns:
            Dictionary with total scans, findings counts, etc.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total scans
            cursor.execute("SELECT COUNT(*) FROM scans")
            total_scans = cursor.fetchone()[0]
            
            # Total findings
            cursor.execute("SELECT COUNT(*) FROM findings")
            total_findings = cursor.fetchone()[0]
            
            # Severity breakdown
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM findings
                GROUP BY severity
            """)
            severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_scans': total_scans,
                'total_findings': total_findings,
                'severity_counts': severity_counts
            }
