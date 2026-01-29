"""
Quick test to verify CSV parsing improvements
"""
import pandas as pd
from io import StringIO

# Test 1: Standard CSV with commas
print("Test 1: Standard CSV with commas")
csv_data = """Query,Page,Clicks,Impressions,Position
python programming,https://example.com/python,150,1250,5.6
web development,https://example.com/web-dev,178,1780,7.8"""

try:
    df = pd.read_csv(StringIO(csv_data), on_bad_lines='skip', engine='python')
    print(f"[PASS] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}\n")
except Exception as e:
    print(f"[FAIL] {e}\n")

# Test 2: CSV with inconsistent fields (simulating the error scenario)
print("Test 2: CSV with inconsistent fields (bad lines)")
csv_data_bad = """Query
python programming,https://example.com/python,150,1250,5.6
web development
javascript,https://example.com/js,200,2000,8.5"""

try:
    df = pd.read_csv(StringIO(csv_data_bad), on_bad_lines='skip', engine='python')
    print(f"[PASS] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    print("Note: Bad lines were skipped as expected\n")
except Exception as e:
    print(f"[FAIL] {e}\n")

# Test 3: Tab-delimited data
print("Test 3: Tab-delimited CSV")
csv_data_tab = "Query\tPage\tClicks\npython\thttps://example.com\t150\njs\thttps://example.com/js\t200"

try:
    df = pd.read_csv(StringIO(csv_data_tab), sep='\t', on_bad_lines='skip', engine='python')
    print(f"[PASS] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}\n")
except Exception as e:
    print(f"[FAIL] {e}\n")

# Test 4: Reading the sample file
print("Test 4: Reading sample_gsc_data.csv")
try:
    df = pd.read_csv('sample_gsc_data.csv', on_bad_lines='skip', engine='python')
    print(f"[PASS] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"First few rows:\n{df.head(3)}")
except Exception as e:
    print(f"[FAIL] {e}")

print("\n[DONE] All tests completed!")
