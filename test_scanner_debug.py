"""
Test Web Scanner Direct
Debug why scan returns 0 findings
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "services" / "scanner-core"))

from web_scanner import WebScanner
from llm_analyzer import LLMAnalyzer
from api_key_manager import APIKeyManager

async def test_scan():
    # Init components
    api_mgr = APIKeyManager()
    llm = LLMAnalyzer(api_mgr, 'gemini')
    scanner = WebScanner(llm, max_depth=1, max_pages=5)
    
    # Test crawl directly
    print("=" * 60)
    print("TESTING WEB SCANNER DIRECT")
    print("=" * 60)
    
    test_url = "https://unisbablitar.ac.id/"
    print(f"\nTarget: {test_url}")
    print(f"Testing _crawl() method...\n")
    
    try:
        # Test crawl
        import aiohttp
        async with aiohttp.ClientSession() as session:
            scanner.session = session
            pages = await scanner._crawl(test_url)
            print(f"\n✓ Crawl successful!")
            print(f"  Pages found: {len(pages)}")
            for i, page in enumerate(pages[:3]):  # Show first 3
                print(f"    {i+1}. {page['url']} ({page.get('status', 'N/A')})")
            
            if not pages:
                print("\n⚠️ WARNING: _crawl() returned EMPTY list!")
                print("   This is why scan shows 0 findings!")
            
    except Exception as e:
        print(f"\n❌ ERROR during crawl:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_scan())
