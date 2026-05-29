import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto('https://www.kaggle.com/datasets/nih-chest-xrays/data')
        
        # Wait for the page to load
        await page.wait_for_timeout(5000)
        
        # Try to hide cookie banners if any
        try:
            await page.evaluate("""
                const elements = document.querySelectorAll('[role="dialog"], .cookie-banner');
                for (let el of elements) el.style.display = 'none';
            """)
        except:
            pass
            
        await page.screenshot(path='D:\\My\\ppt-master\\projects\\xai_medical_ppt169_20260529\\images\\kaggle_screenshot.png')
        await browser.close()
        print("Screenshot saved to kaggle_screenshot.png")

asyncio.run(main())
