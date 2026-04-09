"""
Standalone debug script — NO pytest, NO class, NO fixtures.

Run directly from PyCharm terminal:
    python debug_zoomcar.py

This opens Chrome, selects Chennai, picks dates, then prints
ALL elements on screen so we can find the exact time slider selector.
"""

from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_URL       = "https://www.zoomcar.com"
START_DATE_DAY = str((datetime.now() + timedelta(days=1)).day)
END_DATE_DAY   = str((datetime.now() + timedelta(days=2)).day)
START_DISPLAY  = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
END_DISPLAY    = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")


def run():
    with sync_playwright() as p:

        # ── Launch Chrome ────────────────────────────────────────────────────
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            slow_mo=600,
            args=["--start-maximized"]
        )
        context = browser.new_context(
            viewport=None,
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )
        page = context.new_page()

        print("\n" + "="*60)
        print("  ZOOMCAR DEBUG — Time Slider Inspector")
        print("="*60)

        # ── Step 1: Open homepage ────────────────────────────────────────────
        print("\n[1] Opening Zoomcar homepage...")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        # Wait for JS/React to fully render after DOM loads
        page.wait_for_timeout(3000)
        print(f"   Page loaded: {page.url}")

        # Dismiss any popups
        for sel in [
            'button:has-text("Accept")', 'button:has-text("Close")',
            'button:has-text("Not Now")', 'button:has-text("Skip")',
            '[aria-label="Close"]',
        ]:
            el = page.locator(sel).first
            if el.is_visible():
                el.click()
                page.wait_for_timeout(300)

        # ── Step 2: Select Chennai ───────────────────────────────────────────
        print("\n[2] Selecting Chennai...")
        city_found = False
        for sel in [
            'input[placeholder*="city" i]',
            'input[placeholder*="location" i]',
            'input[placeholder*="search" i]',
            '[class*="city" i] input',
            '[class*="location" i] input',
        ]:
            el = page.locator(sel).first
            if el.is_visible():
                el.click()
                page.wait_for_timeout(300)
                el.fill("Chennai")
                page.wait_for_timeout(1000)
                print(f"   City input found: {sel}")
                city_found = True
                break

        if city_found:
            for opt_sel in [
                'li:has-text("Chennai")',
                '[role="option"]:has-text("Chennai")',
                '[class*="option" i]:has-text("Chennai")',
                '[class*="item" i]:has-text("Chennai")',
                'div:has-text("Chennai")',
            ]:
                try:
                    opt = page.locator(opt_sel).first
                    opt.wait_for(state="visible", timeout=2000)
                    opt.click()
                    print(f"   Chennai selected via: {opt_sel}")
                    break
                except Exception:
                    continue
        else:
            print("   ⚠️  City input not found!")

        page.wait_for_timeout(800)

        # ── Step 3: Click the home button to open date-time modal ─────────────
        print("\n[3] Opening date-time modal via home button...")
        btn = page.locator('[class*="home" i] button').first
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        page.wait_for_timeout(1000)
        print("   ✅ Modal opened")

        # ── Step 4: Inspect sliders IMMEDIATELY after modal opens ─────────────
        print("\n[4] Checking for range sliders right after modal opens...")
        sliders = page.locator('input[type="range"]').all()
        print(f"   Found {len(sliders)} range slider(s)")
        for i, sl in enumerate(sliders):
            try:
                name = sl.get_attribute("name") or "?"
                mn   = sl.get_attribute("min")  or "?"
                mx   = sl.get_attribute("max")  or "?"
                val  = sl.evaluate("el => el.value")
                vis  = sl.is_visible()
                cls  = (sl.get_attribute("class") or "")[:60]
                print(f"   [{i}] name={name}  min={mn}  max={mx}  val={val}  visible={vis}  class={cls}")
            except Exception as e:
                print(f"   [{i}] error: {e}")

        # ── Step 5: Click start date (Today+1) ───────────────────────────────
        print(f"\n[5] Clicking start date: {START_DISPLAY} (day={START_DATE_DAY})...")
        # ── Step 6: Click start date (Today+1) after inspecting sliders ──────
        print(f"\n[4] Clicking start date: {START_DISPLAY} (day={START_DATE_DAY})...")
        for sel in [
            f'[role="gridcell"]:has-text("{START_DATE_DAY}")',
            f'[role="cell"]:has-text("{START_DATE_DAY}")',
            f'[class*="day" i]:has-text("{START_DATE_DAY}")',
            f'td:has-text("{START_DATE_DAY}")',
            f'button:has-text("{START_DATE_DAY}")',
            f'abbr:has-text("{START_DATE_DAY}")',
            f'span:has-text("{START_DATE_DAY}")',
        ]:
            cells = page.locator(sel)
            for i in range(cells.count()):
                cell = cells.nth(i)
                if cell.is_visible() and cell.is_enabled():
                    cell.click()
                    page.wait_for_timeout(500)
                    print(f"   Start date clicked via: {sel}")
                    break
            else:
                continue
            break

        # ── Step 7: Click end date (Today+2) ───────────────────────────────
        print(f"\n[5] Clicking end date: {END_DISPLAY} (day={END_DATE_DAY})...")
        for sel in [
            f'[role="gridcell"]:has-text("{END_DATE_DAY}")',
            f'[role="cell"]:has-text("{END_DATE_DAY}")',
            f'[class*="day" i]:has-text("{END_DATE_DAY}")',
            f'td:has-text("{END_DATE_DAY}")',
            f'button:has-text("{END_DATE_DAY}")',
            f'abbr:has-text("{END_DATE_DAY}")',
            f'span:has-text("{END_DATE_DAY}")',
        ]:
            cells = page.locator(sel)
            for i in range(cells.count()):
                cell = cells.nth(i)
                if cell.is_visible() and cell.is_enabled():
                    cell.click()
                    page.wait_for_timeout(500)
                    print(f"   End date clicked via: {sel}")
                    break
            else:
                continue
            break

        page.wait_for_timeout(1000)

        # ── Step 8: Re-check sliders after both dates clicked ────────────────
        print("\n[8] Re-checking range sliders after dates selected...")
        sliders2 = page.locator('input[type="range"]').all()
        print(f"   Found {len(sliders2)} range slider(s) after date selection")
        for i, sl in enumerate(sliders2):
            try:
                name = sl.get_attribute("name") or "?"
                mn   = sl.get_attribute("min")  or "?"
                mx   = sl.get_attribute("max")  or "?"
                val  = sl.evaluate("el => el.value")
                vis  = sl.is_visible()
                cls  = (sl.get_attribute("class") or "")[:60]
                print(f"   [{i}] name={name}  min={mn}  max={mx}  val={val}  visible={vis}  class={cls}")
            except Exception as e:
                print(f"   [{i}] error: {e}")

        # ── Step 9: Take screenshot BEFORE waiting ───────────────────────────
        page.screenshot(path="debug_after_dates.png", full_page=True)
        print("\n📸 Screenshot saved → debug_after_dates.png")
        print("\n👀 Check the browser window — is the time slider visible?")
        print("   Waiting 4 seconds for any delayed UI to appear...")
        page.wait_for_timeout(4000)
        page.screenshot(path="debug_after_wait.png", full_page=True)
        print("📸 Second screenshot → debug_after_wait.png")

        # ── Step 7: Print ALL input elements ─────────────────────────────────
        print("\n" + "─"*60)
        print("  ALL VISIBLE <input> ELEMENTS ON PAGE")
        print("─"*60)
        for i, el in enumerate(page.locator("input").all()):
            try:
                if not el.is_visible():
                    continue
                t    = el.get_attribute("type")        or "?"
                name = el.get_attribute("name")        or "?"
                cls  = (el.get_attribute("class")      or "")[:70]
                pid  = el.get_attribute("data-testid") or "?"
                mn   = el.get_attribute("min")         or "?"
                mx   = el.get_attribute("max")         or "?"
                val  = el.evaluate("el => el.value")   or "?"
                print(f"  [{i:02d}] type={t:<8} name={name:<15} "
                      f"min={mn:<4} max={mx:<4} val={val:<5} "
                      f"testid={pid:<20} class={cls}")
            except Exception:
                pass

        # ── Step 8: Print ALL range sliders ──────────────────────────────────
        print("\n" + "─"*60)
        print("  ALL <input type='range'> SLIDERS (visible + hidden)")
        print("─"*60)
        sliders = page.locator('input[type="range"]').all()
        if not sliders:
            print("  ❌ NONE FOUND")
        for i, el in enumerate(sliders):
            try:
                name = el.get_attribute("name")    or "?"
                mn   = el.get_attribute("min")     or "?"
                mx   = el.get_attribute("max")     or "?"
                step = el.get_attribute("step")    or "?"
                val  = el.evaluate("el => el.value") or "?"
                vis  = el.is_visible()
                cls  = (el.get_attribute("class")  or "")[:70]
                pid  = el.get_attribute("data-testid") or "?"
                print(f"  [{i}] name={name}  min={mn}  max={mx}  step={step}"
                      f"  val={val}  visible={vis}  testid={pid}  class={cls}")
            except Exception as e:
                print(f"  [{i}] ERROR: {e}")

        # ── Step 9: Count time-related elements ──────────────────────────────
        print("\n" + "─"*60)
        print("  TIME-RELATED ELEMENT COUNTS")
        print("─"*60)
        for sel in [
            'input[type="range"]',
            'input[type="time"]',
            'input[name*="time" i]',
            '[class*="time" i]',
            '[class*="Time"]',
            '[data-testid*="time" i]',
            '[aria-label*="time" i]',
            'select[name*="time" i]',
        ]:
            c = page.locator(sel).count()
            if c > 0:
                print(f"  {c:3d}x  →  {sel}")

        # ── Step 10: Modal / overlay state ───────────────────────────────────
        print("\n" + "─"*60)
        print("  MODAL / PICKER / OVERLAY STATE")
        print("─"*60)
        for sel in [
            '[role="dialog"]', '[class*="modal" i]',
            '[class*="picker" i]', '[class*="calendar" i]',
            '[class*="overlay" i]', '[class*="DateRange" i]',
            '[class*="TimePicker" i]',
        ]:
            el = page.locator(sel).first
            if el.is_visible():
                cls = (el.get_attribute("class") or "")[:80]
                print(f"  VISIBLE: {sel}  →  class={cls}")

        print("\n" + "="*60)
        print("  DEBUG COMPLETE")
        print("  📋 Copy ALL output above and share it to fix the slider")
        print("="*60)

        input("\n⏸  Press ENTER to close the browser...")
        browser.close()


if __name__ == "__main__":
    run()
