import traceback
import sys

# Test calling get_stats and get_complaint_clusters internally
try:
    from main import get_stats, get_complaint_clusters
    print("Calling get_stats directly...")
    res = get_stats("admin@grievanceiq.in")
    print("Success get_stats:", res.keys())
except Exception as e:
    print("Exception in get_stats:")
    traceback.print_exc()

try:
    print("\nCalling get_complaint_clusters directly...")
    res_c = get_complaint_clusters("admin@grievanceiq.in")
    print("Success get_complaint_clusters:", len(res_c.get("clusters", [])))
except Exception as e:
    print("Exception in get_complaint_clusters:")
    traceback.print_exc()
