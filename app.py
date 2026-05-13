import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

USERS_API = "https://users.roblox.com"
THUMBNAILS_API = "https://thumbnails.roblox.com"
GROUPS_API = "https://groups.roblox.com"
FRIENDS_API = "https://friends.roblox.com"
GAMES_API = "https://games.roblox.com"
ACCOUNT_INFO_API = "https://accountinformation.roblox.com"

TIMEOUT = 10


def safe(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        return None


def format_number(n):
    if not isinstance(n, int):
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,}"


def account_age(created_str: str) -> dict:
    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - created
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = diff.days % 30
    pct = min(100, int(diff.days / 3650 * 100))
    return {
        "years": years,
        "months": months,
        "days": days,
        "total_days": diff.days,
        "pct": pct,
    }


def get_user_by_username(username: str):
    resp = requests.post(
        f"{USERS_API}/v1/usernames/users",
        json={"usernames": [username], "excludeBannedUsers": False},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return data[0] if data else None


def get_user_details(user_id: int) -> dict:
    resp = requests.get(f"{USERS_API}/v1/users/{user_id}", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_avatar_headshot(user_id: int):
    resp = requests.get(
        f"{THUMBNAILS_API}/v1/users/avatar-headshot",
        params={"userIds": user_id, "size": "420x420", "format": "Png", "isCircular": "true"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return data[0].get("imageUrl") if data else None


def get_avatar_full(user_id: int):
    resp = requests.get(
        f"{THUMBNAILS_API}/v1/users/avatar",
        params={"userIds": user_id, "size": "420x420", "format": "Png", "isCircular": "false"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return data[0].get("imageUrl") if data else None


def get_groups(user_id: int) -> list:
    resp = requests.get(f"{GROUPS_API}/v2/users/{user_id}/groups/roles", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("data", [])


def get_group_icons(group_ids: list) -> dict:
    resp = requests.get(
        f"{THUMBNAILS_API}/v1/groups/icons",
        params={"groupIds": group_ids, "size": "150x150", "format": "Png"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return {
        item["targetId"]: item.get("imageUrl")
        for item in resp.json().get("data", [])
    }


def get_friends_count(user_id: int) -> int:
    resp = requests.get(f"{FRIENDS_API}/v1/users/{user_id}/friends/count", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("count", 0)


def get_followers_count(user_id: int) -> int:
    resp = requests.get(f"{FRIENDS_API}/v1/users/{user_id}/followers/count", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("count", 0)


def get_following_count(user_id: int) -> int:
    resp = requests.get(f"{FRIENDS_API}/v1/users/{user_id}/followings/count", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("count", 0)


def get_roblox_badges(user_id: int) -> list:
    resp = requests.get(
        f"{ACCOUNT_INFO_API}/v1/users/{user_id}/roblox-badges",
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def get_user_games(user_id: int) -> list:
    resp = requests.get(
        f"{GAMES_API}/v2/users/{user_id}/games",
        params={"sortOrder": "Desc", "limit": 10},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def get_game_thumbnails(universe_ids: list) -> dict:
    resp = requests.get(
        f"{THUMBNAILS_API}/v1/games/multiget/thumbnails",
        params={
            "universeIds": universe_ids,
            "size": "768x432",
            "format": "Png",
            "isCircular": "false",
            "countPerUniverse": 1,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    result = {}
    for entry in resp.json().get("data", []):
        thumbs = entry.get("thumbnails", [])
        if thumbs:
            result[entry["universeId"]] = thumbs[0].get("imageUrl")
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    username = request.args.get("username", "").strip()
    if not username:
        return redirect(url_for("index"))
    return redirect(url_for("profile", username=username))


@app.route("/user/<username>")
def profile(username: str):
    try:
        basic = get_user_by_username(username)
        if not basic:
            return render_template(
                "index.html",
                error=f"User '{username}' was not found on Roblox.",
                searched=username,
            )

        uid = basic["id"]
        details = get_user_details(uid)

        headshot = safe(get_avatar_headshot, uid)
        full_body = safe(get_avatar_full, uid)

        friends = safe(get_friends_count, uid)
        followers = safe(get_followers_count, uid)
        following = safe(get_following_count, uid)

        groups = safe(get_groups, uid) or []
        if groups:
            group_ids = [g["group"]["id"] for g in groups]
            icons = safe(get_group_icons, group_ids) or {}
            for g in groups:
                g["icon"] = icons.get(g["group"]["id"])
        groups = groups[:12]

        games = safe(get_user_games, uid) or []
        games = games[:6]
        if games:
            universe_ids = [g["id"] for g in games]
            thumbnails = safe(get_game_thumbnails, universe_ids) or {}
            for g in games:
                g["thumbnail"] = thumbnails.get(g["id"])

        roblox_badges = safe(get_roblox_badges, uid) or []

        created_dt = datetime.fromisoformat(details["created"].replace("Z", "+00:00"))
        created_display = created_dt.strftime("%B %d, %Y")
        age = account_age(details["created"])

        user = {
            "id": uid,
            "username": details["name"],
            "display_name": details["displayName"],
            "description": (details.get("description") or "").strip(),
            "created": created_display,
            "age": age,
            "is_banned": details.get("isBanned", False),
            "verified": details.get("hasVerifiedBadge", False),
            "headshot": headshot,
            "full_body": full_body,
            "groups": groups,
            "friends": friends,
            "followers": followers,
            "following": following,
            "friends_fmt": format_number(friends),
            "followers_fmt": format_number(followers),
            "following_fmt": format_number(following),
            "badges": roblox_badges,
            "games": games,
            "profile_url": f"https://www.roblox.com/users/{uid}/profile",
        }

        return render_template("profile.html", user=user)

    except requests.exceptions.ConnectionError:
        error = "Could not connect to the Roblox API. Check your internet connection."
    except requests.exceptions.Timeout:
        error = "The request timed out. Please try again."
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else "?"
        error = f"Roblox API returned an error ({code}). Please try again later."
    except Exception as exc:
        error = f"An unexpected error occurred: {exc}"

    return render_template("index.html", error=error, searched=username)


@app.route("/api/user/<username>")
def api_user(username: str):
    try:
        basic = get_user_by_username(username)
        if not basic:
            return jsonify({"error": "User not found"}), 404

        uid = basic["id"]
        details = get_user_details(uid)
        headshot = safe(get_avatar_headshot, uid)
        friends = safe(get_friends_count, uid)
        followers = safe(get_followers_count, uid)
        following = safe(get_following_count, uid)
        groups = safe(get_groups, uid) or []

        return jsonify({
            "id": uid,
            "username": details["name"],
            "displayName": details["displayName"],
            "description": details.get("description", ""),
            "created": details["created"],
            "isBanned": details.get("isBanned", False),
            "hasVerifiedBadge": details.get("hasVerifiedBadge", False),
            "avatar": headshot,
            "friends": friends,
            "followers": followers,
            "following": following,
            "groupCount": len(groups),
            "profileUrl": f"https://www.roblox.com/users/{uid}/profile",
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, port=5000)
