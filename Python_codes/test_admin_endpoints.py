import requests

try:
    login_res = requests.post("http://127.0.0.1:8000/auth/admin/login", json={"email": "admin@grievanceiq.in", "password": "admin123"})
    print("Admin login status:", login_res.status_code)
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    stats_res = requests.get("http://127.0.0.1:8000/admin/stats", headers=headers)
    print("Stats status:", stats_res.status_code)
    if stats_res.status_code == 200:
        d = stats_res.json()
        print("Stats summary:", {k: d[k] for k in ["total", "open_count", "resolved_count", "escalated_count"]})
        print("Department breakdown count:", len(d.get("department_breakdown", [])))
        print("Company counts count:", len(d.get("company_counts", [])))
    else:
        print("Stats error:", stats_res.text)

    clusters_res = requests.get("http://127.0.0.1:8000/admin/complaint-clusters", headers=headers)
    print("\nClusters status:", clusters_res.status_code)
    if clusters_res.status_code == 200:
        c_data = clusters_res.json()
        print("Total analyzed:", c_data.get("total_analyzed"))
        print("Clusters found:", len(c_data.get("clusters", [])))
        for cl in c_data.get("clusters", []):
            print(" -", cl.get("cluster_title"), "count:", cl.get("count"), "samples:", len(cl.get("sample_complaints", [])))
    else:
        print("Clusters error:", clusters_res.text)

except Exception as e:
    print("Error:", e)
