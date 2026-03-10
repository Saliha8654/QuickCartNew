import sys
import os

# Mock the modules needed by weight_sensor
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def parse_weight_line(line):
    # Centralized parsing logic for weight sensor lines (copied from weight_sensor.py)
    # 1. Try JSON parsing first
    try:
        import json
        data = json.loads(line)
        if isinstance(data, dict):
            if 'weight_g' in data: return float(data['weight_g'])
            if 'weight' in data: return float(data['weight'])
    except:
        pass

    # 2. Try parsing "Weight: 23.45g" format
    if "Weight:" in line:
        import re
        match = re.search(r"Weight:\s*([-+]?\d*\.?\d+)", line)
        if match: return float(match.group(1))
    
    # 3. If we see a number followed by 'g' or 'grams'
    import re
    match = re.search(r"([-+]?\d*\.?\d+)\s*(g|grams)", line.lower())
    if match: return float(match.group(1))

    # 4. Pure numeric
    clean_line = line.replace("g", "").replace("grams", "").strip()
    if clean_line.replace(".", "").replace("-", "").isdigit() and len(line) < 15:
        try:
            return float(clean_line)
        except:
            pass
            
    return None

test_cases = [
    ("Weight: 123.00g", 123.0),
    ("Weight: 122.50g", 122.5),
    ("Weight: 0.00g", 0.0),
    ("Weight: -1.02g", -1.02),
    ("1008.00g", 1008.0),
    ("Weight: 24g", 24.0),
    ("Taring...", None),
    ("Tare DONE!", None),
    ("NOT CALIBRATED — send: c123", None)
]

print("Testing weight parsing logic...")
print("-" * 40)
success = True
for line, expected in test_cases:
    actual = parse_weight_line(line)
    status = "✅" if actual == expected else "❌"
    print(f"{status} Line: '{line}' | Expected: {expected} | Actual: {actual}")
    if actual != expected:
        success = False

print("-" * 40)
if success:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED!")
