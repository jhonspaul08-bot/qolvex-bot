"""
╔══════════════════════════════════════════════════════╗
║         QOLVEX AUTO BOT v2 - No Browser             ║
║      Pure requests — works di Codespaces/VPS        ║
╚══════════════════════════════════════════════════════╝
"""

import requests
import os
import sys
import time
import random
import json
from dotenv import load_dotenv

load_dotenv()

# ── Ambil token ──────────────────────────────────────
def get_tokens():
    auth_token = os.getenv("TWITTER_AUTH_TOKEN", "").strip()
    ct0        = os.getenv("TWITTER_CT0", "").strip()

    if not auth_token or not ct0:
        print("\n╔══════════════════════════════════════════╗")
        print("║         MASUKKAN TOKEN TWITTER           ║")
        print("╠══════════════════════════════════════════╣")
        print("║  F12 → Application → Cookies → twitter  ║")
        print("╚══════════════════════════════════════════╝\n")
        if not auth_token:
            auth_token = input("  → Masukkan auth_token : ").strip()
        if not ct0:
            ct0 = input("  → Masukkan ct0         : ").strip()

    if not auth_token or not ct0:
        print("\n[ERROR] Token tidak boleh kosong!")
        sys.exit(1)

    return auth_token, ct0

# ── Colors ───────────────────────────────────────────
G="\033[92m"; Y="\033[93m"; R="\033[91m"
C="\033[96m"; M="\033[95m"; RS="\033[0m"

def log_ok(m):   print(f"{G}[✓]{RS} {m}")
def log_warn(m): print(f"{Y}[⚠]{RS} {m}")
def log_err(m):  print(f"{R}[✗]{RS} {m}")
def log_info(m): print(f"{C}[→]{RS} {m}")
def log_task(m): print(f"{M}[★]{RS} {m}")

def delay(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))

# ── Twitter Bearer Token (public static) ─────────────
BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I6xoY%2FWEi4%3DEaljkJU43X15cPFi7JLqIxAeFLCrFSUqSblSVCFuSWXWytfXQ"

def twitter_headers(ct0, auth_token):
    return {
        "Authorization"            : f"Bearer {BEARER}",
        "x-csrf-token"             : ct0,
        "x-twitter-auth-type"      : "OAuth2Session",
        "x-twitter-active-user"    : "yes",
        "x-twitter-client-language": "en",
        "Content-Type"             : "application/json",
        "Referer"                  : "https://twitter.com/",
        "User-Agent"               : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

def twitter_cookies(auth_token, ct0):
    return {"auth_token": auth_token, "ct0": ct0}

# ── Get User ID dari username ─────────────────────────
def get_user_id(username: str, auth_token: str, ct0: str) -> str | None:
    variables = json.dumps({
        "screen_name": username,
        "withSafetyModeUserFields": True
    })
    features = json.dumps({
        "hidden_profile_likes_enabled": True,
        "hidden_profile_subscriptions_enabled": True,
        "rweb_tipjar_consumption_enabled": True,
        "verified_phone_label_enabled": False,
        "subscriptions_verification_info_is_identity_verified_enabled": True,
        "subscriptions_verification_info_verified_since_enabled": True,
        "highlights_tweets_tab_ui_enabled": True,
        "responsive_web_twitter_article_notes_tab_enabled": True,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
    })
    try:
        r = requests.get(
            "https://twitter.com/i/api/graphql/G3KGOASz96M-Qu0nwmGXNg/UserByScreenName",
            params={"variables": variables, "features": features},
            headers=twitter_headers(ct0, auth_token),
            cookies=twitter_cookies(auth_token, ct0),
            timeout=15
        )
        data = r.json()
        return data["data"]["user"]["result"]["rest_id"]
    except Exception as e:
        log_warn(f"Gagal get user_id @{username}: {e}")
        return None

# ── Extract Tweet ID dari URL ─────────────────────────
def extract_tweet_id(url: str) -> str | None:
    import re
    m = re.search(r"/status/(\d+)", url)
    return m.group(1) if m else None

# ── Follow User ───────────────────────────────────────
def twitter_follow(username: str, auth_token: str, ct0: str) -> bool:
    log_info(f"Follow @{username}...")
    user_id = get_user_id(username, auth_token, ct0)
    if not user_id:
        log_warn(f"User ID tidak ditemukan untuk @{username}, skip")
        return True

    try:
        r = requests.post(
            "https://twitter.com/i/api/1.1/friendships/create.json",
            data={"user_id": user_id, "skip_status": True},
            headers={
                **twitter_headers(ct0, auth_token),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            cookies=twitter_cookies(auth_token, ct0),
            timeout=15
        )
        if r.status_code == 200:
            log_ok(f"Followed @{username}")
            return True
        else:
            log_warn(f"Follow @{username} status: {r.status_code} — {r.text[:100]}")
            return True  # tetap lanjut
    except Exception as e:
        log_warn(f"Error follow @{username}: {e}")
        return True

# ── Like Tweet ────────────────────────────────────────
def twitter_like(tweet_url: str, auth_token: str, ct0: str) -> bool:
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        log_warn(f"Tweet ID tidak ditemukan dari URL: {tweet_url}")
        return True

    log_info(f"Like tweet ID: {tweet_id}...")
    try:
        r = requests.post(
            "https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",
            json={
                "variables": {"tweet_id": tweet_id},
                "queryId": "lI07N6Otwv1PhnEgXILM7A"
            },
            headers=twitter_headers(ct0, auth_token),
            cookies=twitter_cookies(auth_token, ct0),
            timeout=15
        )
        if r.status_code == 200:
            log_ok(f"Liked tweet {tweet_id}")
        else:
            log_warn(f"Like status: {r.status_code} — {r.text[:100]}")
        return True
    except Exception as e:
        log_warn(f"Error like: {e}")
        return True

# ── Retweet ───────────────────────────────────────────
def twitter_retweet(tweet_url: str, auth_token: str, ct0: str) -> bool:
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        log_warn(f"Tweet ID tidak ditemukan dari URL: {tweet_url}")
        return True

    log_info(f"Retweet tweet ID: {tweet_id}...")
    try:
        r = requests.post(
            "https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet",
            json={
                "variables": {"tweet_id": tweet_id, "dark_request": False},
                "queryId": "ojPdsZsimiJrUGLR1sjUtA"
            },
            headers=twitter_headers(ct0, auth_token),
            cookies=twitter_cookies(auth_token, ct0),
            timeout=15
        )
        if r.status_code == 200:
            log_ok(f"Retweeted tweet {tweet_id}")
        else:
            log_warn(f"Retweet status: {r.status_code} — {r.text[:100]}")
        return True
    except Exception as e:
        log_warn(f"Error retweet: {e}")
        return True

# ── Qolvex OAuth Flow (no browser) ───────────────────
def qolvex_login(auth_token: str, ct0: str) -> requests.Session | None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer"   : "https://qolvex.xyz/login",
    })

    log_info("Mulai OAuth flow ke Qolvex...")

    # Step 1: GET /api/auth/twitter → dapat redirect URL ke Twitter
    r1 = session.get("https://qolvex.xyz/api/auth/twitter",
                     allow_redirects=False, timeout=15)

    oauth_url = r1.headers.get("Location") or r1.json().get("url", "")

    if not oauth_url or "twitter.com" not in oauth_url and "x.com" not in oauth_url:
        log_warn(f"Tidak dapat OAuth URL: {r1.status_code} {r1.text[:200]}")
        return None

    log_info(f"OAuth URL: {oauth_url[:80]}...")

    # Step 2: GET OAuth URL dengan Twitter cookies → Twitter langsung approve
    tw_session = requests.Session()
    tw_session.cookies.set("auth_token", auth_token, domain=".twitter.com")
    tw_session.cookies.set("ct0",        ct0,        domain=".twitter.com")
    tw_session.cookies.set("auth_token", auth_token, domain=".x.com")
    tw_session.cookies.set("ct0",        ct0,        domain=".x.com")
    tw_session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-csrf-token": ct0,
    })

    r2 = tw_session.get(oauth_url, allow_redirects=True, timeout=20)
    final_url = r2.url

    log_info(f"Setelah OAuth URL: {final_url[:80]}...")

    # Cari callback code
    code = None
    if "code=" in final_url:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(final_url)
        code = parse_qs(parsed.query).get("code", [None])[0]

    if not code and "qolvex.xyz/callback" in final_url:
        # Sudah di callback, ambil dari URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(final_url)
        code = parse_qs(parsed.query).get("code", [None])[0]

    if not code:
        # Coba cek apakah ada approve button yang perlu di-handle
        # Twitter kadang redirect langsung ke callback kalau sudah pernah authorize
        log_warn("Code tidak ditemukan di redirect URL")
        log_info(f"Response URL: {r2.url}")
        log_info(f"Response preview: {r2.text[:300]}")
        return None

    log_ok(f"OAuth code didapat: {code[:20]}...")

    # Step 3: Exchange code → session cookie Qolvex
    r3 = session.get(
        f"https://qolvex.xyz/api/auth/exchange",
        params={"code": code},
        timeout=15
    )

    log_info(f"Exchange response: {r3.status_code} {r3.text[:200]}")

    if r3.status_code == 200:
        data = r3.json()
        if data.get("success"):
            log_ok("Login Qolvex berhasil! 🎉")
            return session
        else:
            log_err(f"Exchange gagal: {data}")
            return None
    else:
        log_err(f"Exchange HTTP {r3.status_code}: {r3.text[:200]}")
        return None


# ── Main Bot ──────────────────────────────────────────
def run_bot():
    print(f"""
{M}╔══════════════════════════════════════════════════════╗
║         QOLVEX AUTO BOT v2 - No Browser             ║
╚══════════════════════════════════════════════════════╝{RS}
""")

    auth_token, ct0 = get_tokens()
    log_ok("Token diterima!\n")

    # Login
    session = qolvex_login(auth_token, ct0)
    if not session:
        log_err("Login gagal. Cek token Twitter kamu.")
        sys.exit(1)

    api_headers = {
        "Referer"   : "https://qolvex.xyz/dashboard",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    # Fetch tasks
    log_info("Fetching tasks...")
    r = session.get("https://qolvex.xyz/api/tasks", headers=api_headers, timeout=15)
    if r.status_code != 200:
        log_err(f"Gagal fetch tasks: {r.status_code} {r.text[:200]}")
        sys.exit(1)

    data  = r.json()
    tasks = data if isinstance(data, list) else data.get("tasks", [])

    # Fetch completed
    done_r = session.get("https://qolvex.xyz/api/tasks/my-completions",
                         headers=api_headers, timeout=15)
    completed_ids = set()
    if done_r.status_code == 200:
        completed_ids = {c.get("taskId") or c.get("id")
                         for c in done_r.json() if c}

    active_tasks = [t for t in tasks
                    if t.get("isActive", True) and t.get("id") not in completed_ids]

    log_ok(f"Total tasks   : {len(tasks)}")
    log_ok(f"Sudah selesai : {len(completed_ids)}")
    log_ok(f"Tasks tersisa : {len(active_tasks)}\n")

    if not active_tasks:
        log_ok("Semua tasks sudah dikerjakan! 🎉")
        sys.exit(0)

    # Kerjakan tasks
    success = 0
    fail    = 0

    for i, task in enumerate(active_tasks, 1):
        task_id   = task.get("id", "")
        task_type = task.get("taskType", task.get("type", "unknown"))
        title     = task.get("title", task.get("description", f"Task #{i}"))
        reward    = task.get("rewardSol", task.get("reward_sol", "?"))

        log_task(f"[{i}/{len(active_tasks)}] {title}")
        log_info(f"  Type: {task_type} | Reward: {reward} SOL")

        # Aksi Twitter
        ok = True
        if task_type == "follow_twitter":
            username = task.get("targetUsername", "")
            if username:
                ok = twitter_follow(username, auth_token, ct0)

        elif task_type == "like_tweet":
            url = task.get("targetTweetUrl") or task.get("targetUrl", "")
            if url:
                ok = twitter_like(url, auth_token, ct0)

        elif task_type == "retweet":
            url = task.get("targetTweetUrl") or task.get("targetUrl", "")
            if url:
                ok = twitter_retweet(url, auth_token, ct0)

        elif task_type in ("visit_url", "join_telegram"):
            url = task.get("targetUrl") or task.get("url", "")
            log_info(f"  Visit (simulated): {url}")
            # Cukup GET saja
            try:
                requests.get(url, timeout=10)
                log_ok(f"  Visited {url}")
            except Exception:
                pass

        else:
            log_warn(f"  Task type tidak dikenal: {task_type}")

        if not ok:
            fail += 1
            print()
            continue

        delay(1, 2)

        # Submit completion
        log_info("  Submit completion ke Qolvex...")
        cr = session.post(
            f"https://qolvex.xyz/api/tasks/{task_id}/complete",
            json={},
            headers={**api_headers, "Content-Type": "application/json"},
            timeout=15
        )

        try:
            result = cr.json()
        except Exception:
            result = {}

        err = result.get("error", "")
        if cr.status_code == 200 and not err:
            log_ok(f"  ✓ Task selesai! +{reward} SOL")
            success += 1
        elif "already" in str(err).lower():
            log_ok(f"  ✓ Sudah dikerjakan sebelumnya")
            success += 1
        else:
            log_warn(f"  Gagal: {err or cr.status_code}")
            fail += 1

        delay(2, 4)
        print()

    # Summary
    print(f"\n{G}{'═'*50}")
    print(f"  SUMMARY")
    print(f"{'═'*50}{RS}")
    log_ok(f"Berhasil : {success}/{len(active_tasks)}")
    if fail:
        log_warn(f"Gagal    : {fail}")

    bal = session.get("https://qolvex.xyz/api/wallet/balance",
                      headers=api_headers, timeout=10)
    if bal.status_code == 200:
        b = bal.json()
        log_ok(f"Balance  : {b.get('balance') or b.get('sol') or b} SOL")

    print(f"{G}{'═'*50}{RS}\n")
    log_ok("Bot selesai!")


if __name__ == "__main__":
    run_bot()
