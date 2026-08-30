"""
Visita cada app de Streamlit Community Cloud con un navegador headless real
(Playwright) para que el JS ejecute y se abra el WebSocket que Streamlit
necesita para contar "tráfico" de verdad. Un simple requests.get() NO sirve:
solo devuelve el HTML estático y nunca despierta ni mantiene despierta la app.

Si la app está dormida, Streamlit muestra un botón de confirmación
("Yes, get this app back up!"). Este script lo detecta y lo clica.
"""

import asyncio
import sys
from playwright.async_api import async_playwright

APPS = [
    "https://aloe-extraction-optimization.streamlit.app",
    "https://efsa-additives-rag.streamlit.app",
    "https://nutriscore2-0.streamlit.app",
]

WAKE_BUTTON_TEXT = "Yes, get this app back up!"
NAV_TIMEOUT_MS = 60_000
WAKE_WAIT_MS = 20_000


async def ping_app(playwright, url: str) -> bool:
    """Devuelve True si la app terminó accesible, False si hubo error."""
    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        if await wake_button.count() > 0:
            print(f"[DORMIDA] {url} -> despertando...")
            await wake_button.click()
            await page.wait_for_timeout(WAKE_WAIT_MS)
            print(f"[OK] {url} -> despertada")
        else:
            print(f"[OK] {url} -> ya estaba despierta")
        return True
    except Exception as exc:
        print(f"[ERROR] {url} -> {exc}", file=sys.stderr)
        return False
    finally:
        await browser.close()


async def main() -> int:
    results = []
    async with async_playwright() as playwright:
        for url in APPS:
            ok = await ping_app(playwright, url)
            results.append(ok)

    if not all(results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
