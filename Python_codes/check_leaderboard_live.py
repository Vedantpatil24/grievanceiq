import requests

login_res = requests.post("http://127.0.0.1:8000/auth/admin/login", json={"email": "admin@grievanceiq.in", "password": "admin123"})
token = login_res.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

for tf in ["monthly", "quarterly", "yearly"]:
    res = requests.get(f"http://127.0.0.1:8000/admin/leaderboard?timeframe={tf}", headers=headers)
    print(f"\n--- Leaderboard ({tf}) Status {res.status_code} ---")
    if res.status_code == 200:
        data = res.json().get("leaderboard", [])
        for item in data[:5]:
            print(f"Rank {item['rank']}: {item['company']:<24} Score: {item['score']} Total: {item['total_complaints']} Resolved: {item['resolved_count']} Escalated: {item['escalated_count']}")
    else:
        print(res.text)
