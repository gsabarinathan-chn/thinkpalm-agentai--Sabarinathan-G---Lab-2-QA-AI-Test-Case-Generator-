import pytest
import os
import base64
from datetime import datetime
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

# ─────────────────────────────────────────────
# REPORT PATH  (always relative to this file)
# ─────────────────────────────────────────────

REPORT_DIR      = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE     = os.path.join(REPORT_DIR, "report.html")
SCREENSHOT_DIR  = os.path.join(REPORT_DIR, "screenshots")


# ─────────────────────────────────────────────
# AUTO-CONFIGURE HTML REPORT
# ─────────────────────────────────────────────

def pytest_configure(config):
    """Force HTML report generation regardless of how pytest is launched."""
    if not config.option.__dict__.get("htmlpath"):
        config.option.htmlpath            = REPORT_FILE
        config.option.self_contained_html = True


def pytest_html_report_title(report):
    report.title = "Zoomcar Chennai – Automation Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([f"<p><b>URL:</b> https://www.zoomcar.com</p>"])
    prefix.extend([
        f"<p><b>City:</b> Chennai &nbsp;|&nbsp; "
        f"<b>Slot:</b> 3:00 PM – 5:00 PM &nbsp;|&nbsp; "
        f"<b>Browser:</b> Google Chrome &nbsp;|&nbsp; "
        f"<b>Run at:</b> {datetime.now().strftime('%d %b %Y  %I:%M %p')}</p>"
    ])


# ─────────────────────────────────────────────
# SCREENSHOT FOR EVERY TEST (pass + fail)
# 1 screenshot per test case = 25 screenshots
# Embedded into report.html with PASS/FAIL label
# ─────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot after EVERY test and embed it in the HTML report."""
    outcome = yield
    report  = outcome.get_result()

    # Only capture at the end of the actual test call (not setup/teardown)
    if report.when != "call":
        return

    page = item.funcargs.get("page")
    if not page:
        return

    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # Build filename: e.g. PASS_TestPageLoad_test_homepage_loads.png
        status    = "PASS" if report.passed else "FAIL"
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
        filename  = f"{status}_{safe_name}.png"
        screenshot_path = os.path.join(SCREENSHOT_DIR, filename)

        # Take screenshot — short timeout so frozen browser never blocks pytest
        page.screenshot(path=screenshot_path, full_page=False, timeout=8000)
        print(f"\n📸 [{status}] Screenshot → screenshots/{filename}")

        # Embed inline into HTML report
        with open(screenshot_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        color  = "#2ecc71" if report.passed else "#e74c3c"
        label  = "✅ PASSED" if report.passed else "❌ FAILED"
        html = (
            f'<div style="margin-top:8px;">'
            f'<p style="color:{color};font-weight:bold;">{label} — Screenshot</p>'
            f'<img src="data:image/png;base64,{encoded}" '
            f'style="max-width:100%;border:2px solid {color};border-radius:4px;" />'
            f'</div>'
        )
        extras = getattr(report, "extras", [])
        try:
            from pytest_html import extras as html_extras
            extras.append(html_extras.html(html))
        except ImportError:
            pass
        report.extras = extras

    except Exception as e:
        # Never let screenshot errors crash pytest
        print(f"\n⚠️  Screenshot skipped for {item.name}: {e}")


# ─────────────────────────────────────────────
# CHROME BROWSER FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Browser:
    """Launch Google Chrome for all tests."""
    browser = playwright.chromium.launch(
        channel="chrome",
        headless=False,
        slow_mo=500,
        args=["--start-maximized"]
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """Fresh browser context per test (incognito-like)."""
    context = browser.new_context(
        viewport=None,
        locale="en-IN",
        timezone_id="Asia/Kolkata"
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """New page per test."""
    page = context.new_page()
    yield page
    page.close()
