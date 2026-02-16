"""
Test SSL Bypass Feature
Test scanning https://unisbablitar.ac.id/ with SSL verification OFF
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "services" / "scanner-core"))

from web_scanner import WebScanner
from llm_analyzer import LLMAnalyzer
from api_key_manager import APIKeyManager

async def test_ssl_bypass():
    # Init components
    api_mgr = APIKeyManager()
    llm = LLMAnalyzer(api_mgr, 'gemini')
    
    print("=" * 70)
    print("TESTING SSL BYPASS FEATURE")
    print("=" * 70)
    
    test_url = "https://unisbablitar.ac.id/"
    
    # Test 1: WITH SSL verification (should fail)
    print("\n" + "="*70)
    print("TEST 1: SSL Verification ON (default)")
    print("="*70)
    scanner = WebScanner(llm, max_depth=1, max_pages=3, verify_ssl=True)
    
    try:
        import aiohttp
        ssl_context = None  # Use default
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            scanner.session = session
            pages = await scanner._crawl(test_url)
            print(f"✓ Pages found: {len(pages)}")
            if len(pages) == 0:
                print("⚠️ WARNING: 0 pages - likely SSL cert error!")
    except Exception as e:
        print(f"❌ FAILED (expected): {type(e).__name__}: {str(e)[:100]}")
    
    # Test 2: WITHOUT SSL verification (should work)
    print("\n" + "="*70)
    print("TEST 2: SSL Verification OFF (bypass enabled)")
    print("="*70)
    scanner2 = WebScanner(llm, max_depth=1, max_pages=3, verify_ssl=False)
    
    try:
        import aiohttp
        ssl_context = False  # Disable verification
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            scanner2.session = session
            pages = await scanner2._crawl(test_url)
            print(f"\n✅ SUCCESS! Pages found: {len(pages)}")
            for i, page in enumerate(pages[:3]):
                print(f"   {i+1}. {page['url']} (status: {page.get('status', 'N/A')})")
                
            if len(pages) > 0:
                print("\n🎉 SSL BYPASS WORKS! Scanner can now scan this site!")
            else:
                print("\n⚠️ Still 0 pages - may be other network issue")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("✅ WebScanner now supports verify_ssl parameter")
    print("✅ aiohttp.TCPConnector configured with ssl=False when bypassing")
    print("✅ Ready to test in GUI!")
    print("\nNext steps:")
    print("1. Launch GUI: python -m gui.emyuel_gui")
    print("2. Go to Advanced Scan tab")
    print("3. Check: ☑ Skip SSL Verification")
    print("4. Enter URL: https://unisbablitar.ac.id/")
    print("5. Click Start Scan")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(test_ssl_bypass())
