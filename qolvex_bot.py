"""
╔══════════════════════════════════════════════════════╗
║           QOLVEX AUTO BOT - by Gumloop AI           ║
║   Auto Login via Twitter + Auto Complete All Tasks  ║
╚══════════════════════════════════════════════════════╝
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import time
import random
import sys
import os
import requests as req

# ── Load .env kalau ada ──────────────────────────────
load_dotenv()

# ── Ambil token dari .env atau minta input manual ───
def get_tokens():
    auth_token = os.getenv("TWITTER_AUTH_TOKEN", "").strip()
    ct0        = os.getenv("TWITTER_CT0", "").strip()

    if not auth_token or not ct0:
        print("\n╔══════════════════════════════════════════╗")
        print("║         MASUKKAN TOKEN TWITTER           ║")
        print("╠══════════════════════════════════════════╣")
        print("║  Cara ambil:                             ║")
        print("║  1. Buka twitter.com (sudah login)       ║")
        print("║  2. F12 → Application → Cookies          ║")
        print("║  3. Copy auth_token dan ct0              ║")
        print("╚══════════════════════════════════════════╝\n")

        if not auth_token:
            auth_token = input("  → Masukkan auth_token : ").strip()
        if not ct0:
            ct0 = input("  → Masukkan ct0         : ").strip()

    if not auth_token or not ct0:
        print("\n[ERROR] Token tidak boleh kosong!")
        sys.exit(1)

    return auth_token, ct0


# ── COLORS ──────────────────────────────────────────
G  = "\033[92m"
Y  = "\033[93m"
R  = "\033[91m"
C  = "\033[96m"
M  = "\033[95m"
W  = "\033[97m"
RS = "\033[0m"

def log_ok(msg):   print(f"{G}[✓]{RS} {msg}")
def log_warn(msg): print(f"{Y}[⚠]{RS} {msg}")
def log_err(msg):  print(f"{R}[✗]{RS} {msg}")
def log_info(msg): print(f"{C}[→]{RS} {msg}")
def log_task(msg): print(f"{M}[★]{RS} {msg}")

def human_delay(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))


# ── AKSI TWITTER ─────────────────────────────────────
def do_twitter_action(context, task_type: str, task_data: dict) -> bool:
    try:
        if task_type == "follow_twitter":
            username = task_data.get("targetUsername", "")
            if not username:
                log_warn("follow_twitter: targetUsername kosong, skip")
                return True

            log_info(f"Follow @{username}...")
            page = context.new_page()
            page.goto(f"https://twitter.com/{username}", timeout=20000)
            human_delay(2, 4)

            try:
                follow_btn = page.locator(
                    '[data-testid="followButton"], '
                    'button[aria-label*="Follow"], '
                    'div[data-testid$="-follow"]'
                ).first
                follow_btn.wait_for(timeout=8000)
                follow_btn.click()
                human_delay(1, 2)
                log_ok(f"Followed @{username}")
            except Exception as e:
                log_warn(f"Tombol follow tidak ditemukan (@{username}): {e}")

            page.close()
            return True

        elif task_type == "like_tweet":
            tweet_url = task_data.get("targetTweetUrl") or task_data.get("targetUrl", "")
            if not tweet_url:
                log_warn("like_tweet: URL kosong, skip")
                return True

            log_info(f"Like tweet: {tweet_url}")
            page = context.new_page()
            page.goto(tweet_url, timeout=20000)
            human_delay(2, 4)

            try:
                like_btn = page.locator('[data-testid="like"]').first
                like_btn.wait_for(timeout=8000)
                like_btn.click()
                human_delay(1, 2)
                log_ok("Liked tweet")
            except Exception as e:
                log_warn(f"Tombol like tidak ditemukan: {e}")

            page.close()
            return True

        elif task_type == "retweet":
            tweet_url = task_data.get("targetTweetUrl") or task_data.get("targetUrl", "")
            if not tweet_url:
                log_warn("retweet: URL kosong, skip")
                return True

            log_info(f"Retweet: {tweet_url}")
            page = context.new_page()
            page.goto(tweet_url, timeout=20000)
            human_delay(2, 4)

            try:
                rt_btn = page.locator('[data-testid="retweet"]').first
                rt_btn.wait_for(timeout=8000)
                rt_btn.click()
                human_delay(0.8, 1.5)

                confirm = page.locator('[data-testid="retweetConfirm"]')
                if confirm.is_visible():
                    confirm.click()
                    human_delay(1, 2)

                log_ok("Retweeted")
            except Exception as e:
                log_warn(f"Tombol retweet tidak ditemukan: {e}")

            page.close()
            return True

        elif task_type in ("visit_url", "join_telegram"):
            url = task_data.get("targetUrl") or task_data.get("url", "")
            if not url:
                log_warn(f"{task_type}: URL kosong, skip")
                return True

            log_info(f"Visit: {url}")
            page = context.new_page()
            try:
                page.goto(url, timeout=20000)
                human_delay(3, 5)
                log_ok(f"Visited {url}")
            except Exception as e:
                log_warn(f"Gagal visit: {e}")
            finally:
                page.close()
            return True

        else:
            log_warn(f"Task type tidak dikenal: {task_type}, skip aksi Twitter")
            return True

    except Exception as e:
        log_err(f"Error do_twitter_action [{task_type}]: {e}")
        return False


# ── MAIN BOT ─────────────────────────────────────────
def run_bot():
    print(f"""
{M}╔══════════════════════════════════════════════════════╗
║           QOLVEX AUTO BOT - by Gumloop AI           ║
╚══════════════════════════════════════════════════════╝{RS}
""")

    TWITTER_AUTH_TOKEN, TWITTER_CT0 = get_tokens()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    DELAY    = int(os.getenv("TASK_DELAY", "3"))

    log_ok("Token diterima, memulai bot...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
        )

        # ── Inject Twitter Cookies ─────────────────────────
        log_info("Injecting Twitter cookies...")
        for domain in [".twitter.com", ".x.com"]:
            context.add_cookies([
                {"name": "auth_token", "value": TWITTER_AUTH_TOKEN, "domain": domain,
                 "path": "/", "httpOnly": True, "secure": True, "sameSite": "None"},
                {"name": "ct0", "value": TWITTER_CT0, "domain": domain,
                 "path": "/", "httpOnly": False, "secure": True, "sameSite": "Lax"},
            ])
        log_ok("Cookies injected")

        # ── OAuth Login Qolvex ─────────────────────────────
        log_info("Membuka Qolvex login...")
        page = context.new_page()
        page.goto("https://qolvex.xyz/login", timeout=30000)
        human_delay(1.5, 2.5)

        log_info("Klik 'Connect with X'...")
        try:
            page.locator("button").filter(has_text="CONNECT WITH X").first.click()
        except Exception:
            page.click("button")
        human_delay(2, 4)

        # ── Tunggu redirect Twitter ─────────────────────────
        for _ in range(15):
            url = page.url
            if "twitter.com" in url or "x.com" in url:
                log_ok(f"Redirect ke Twitter OAuth")
                break
            elif "dashboard" in url:
                log_ok("Langsung masuk dashboard!")
                break
            time.sleep(1)

        # ── Handle Twitter Authorize Page ──────────────────
        if "twitter.com" in page.url or "x.com" in page.url:
            log_info("Handle Twitter OAuth page...")
            human_delay(2, 3)

            for sel in [
                '[data-testid="OAuth_Consent_Button"]',
                'input[id="allow"]',
                'button:has-text("Authorize")',
                'button:has-text("Allow")',
                'input[value="Authorize app"]',
                'button[type="submit"]',
            ]:
                try:
                    el = page.locator(sel).first
                    if el.is_visible():
                        el.click()
                        log_ok(f"Authorize diklik ({sel})")
                        human_delay(2, 4)
                        break
                except Exception:
                    continue

            try:
                page.wait_for_url("**/qolvex.xyz/**", timeout=20000)
            except PlaywrightTimeout:
                pass
            human_delay(2, 3)

        # ── Pastikan di dashboard ───────────────────────────
        if "dashboard" not in page.url:
            page.goto("https://qolvex.xyz/dashboard", timeout=20000)
            human_delay(2, 3)

        if "qolvex.xyz" not in page.url:
            log_err("Gagal login! Cek token Twitter kamu.")
            browser.close()
            return

        log_ok("LOGIN BERHASIL! 🎉\n")

        # ── Ambil session cookies ──────────────────────────
        all_cookies = context.cookies()
        cookie_jar  = {c["name"]: c["value"] for c in all_cookies if "qolvex.xyz" in c["domain"]}
        headers_api = {
            "Referer": "https://qolvex.xyz/dashboard",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # ── Fetch Tasks ────────────────────────────────────
        log_info("Fetching tasks...")
        tasks_resp = req.get("https://qolvex.xyz/api/tasks", cookies=cookie_jar, headers=headers_api, timeout=15)

        if tasks_resp.status_code != 200:
            # Fallback via browser
            log_warn("Fallback fetch tasks via browser...")
            tasks_raw = page.evaluate("""
                async () => {
                    const r = await fetch('/api/tasks', {credentials: 'include'});
                    return await r.json();
                }
            """)
            tasks = tasks_raw if isinstance(tasks_raw, list) else tasks_raw.get("tasks", [])
        else:
            data  = tasks_resp.json()
            tasks = data if isinstance(data, list) else data.get("tasks", [])

        # ── Fetch Completed Tasks ──────────────────────────
        done_resp = req.get("https://qolvex.xyz/api/tasks/my-completions",
                            cookies=cookie_jar, headers=headers_api, timeout=15)
        completed_ids = set()
        if done_resp.status_code == 200:
            completed_ids = {c.get("taskId") or c.get("id") for c in done_resp.json() if c}

        active_tasks = [t for t in tasks if t.get("isActive", True) and t.get("id") not in completed_ids]

        log_ok(f"Total tasks    : {len(tasks)}")
        log_ok(f"Sudah selesai  : {len(completed_ids)}")
        log_ok(f"Tasks tersisa  : {len(active_tasks)}\n")

        if not active_tasks:
            log_ok("Semua tasks sudah dikerjakan! 🎉")
            browser.close()
            return

        # ── Kerjakan Tasks ─────────────────────────────────
        success = 0
        fail    = 0

        for i, task in enumerate(active_tasks, 1):
            task_id    = task.get("id", "")
            task_type  = task.get("taskType", task.get("type", "unknown"))
            task_title = task.get("title", task.get("description", f"Task #{i}"))
            reward     = task.get("rewardSol", task.get("reward_sol", "?"))

            log_task(f"[{i}/{len(active_tasks)}] {task_title}")
            log_info(f"  Type: {task_type} | Reward: {reward} SOL")

            # 1. Aksi Twitter
            ok = do_twitter_action(context, task_type, task)
            if not ok:
                log_warn("  Aksi gagal, skip")
                fail += 1
                continue

            human_delay(1, 2)

            # 2. Submit completion
            log_info("  Submit ke Qolvex API...")
            result = page.evaluate(f"""
                async () => {{
                    const r = await fetch('/api/tasks/{task_id}/complete', {{
                        method: 'POST',
                        credentials: 'include',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{}})
                    }});
                    return await r.json();
                }}
            """)

            err = result.get("error", "")
            if not err or "already" in str(err).lower():
                log_ok(f"  ✓ Selesai! +{reward} SOL")
                success += 1
            else:
                log_warn(f"  Gagal submit: {err}")
                fail += 1

            if i < len(active_tasks):
                time.sleep(DELAY)
            print()

        # ── Summary ────────────────────────────────────────
        print(f"\n{G}{'═'*50}")
        print(f"  SUMMARY")
        print(f"{'═'*50}{RS}")
        log_ok(f"Berhasil : {success}/{len(active_tasks)}")
        if fail:
            log_warn(f"Gagal    : {fail}")

        bal = req.get("https://qolvex.xyz/api/wallet/balance",
                      cookies=cookie_jar, headers=headers_api, timeout=10)
        if bal.status_code == 200:
            b = bal.json()
            log_ok(f"Balance  : {b.get('balance') or b.get('sol') or b} SOL")

        print(f"{G}{'═'*50}{RS}\n")
        browser.close()
        log_ok("Bot selesai!")


if __name__ == "__main__":
    run_bot()
