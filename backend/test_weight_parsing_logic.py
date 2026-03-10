
import unittest
import json
import re

def mock_read_weight(line):
    """Refined version of the parsing logic in weight_sensor.py for testing"""
    line = line.strip()
    if not line: return None
    
    # 1. JSON Parsing
    try:
        data = json.loads(line)
        if isinstance(data, dict):
            if 'weight_g' in data: return float(data['weight_g'])
            if 'weight' in data: return float(data['weight'])
    except: pass

    # 2. "Weight: X" format
    if "Weight:" in line:
        match = re.search(r"Weight:\s*([-+]?\d*\.?\d+)", line)
        if match: return float(match.group(1))

    # 3. Unit format
    match = re.search(r"([-+]?\d*\.?\d+)\s*(g|grams)", line.lower())
    if match: return float(match.group(1))

    # 4. Raw numeric
    clean_line = line.replace("g", "").replace("grams", "").strip()
    if clean_line.replace(".", "").replace("-", "").isdigit() and len(line) < 15:
        return float(clean_line)
    
    return None

class TestWeightParsing(unittest.TestCase):
    def test_json_format(self):
        self.assertEqual(mock_read_weight('{"weight_g": 23.45}'), 23.45)
        self.assertEqual(mock_read_weight('{"weight": 24.0}'), 24.0)

    def test_string_format(self):
        self.assertEqual(mock_read_weight('Weight: 19.0g'), 19.0)
        self.assertEqual(mock_read_weight('Weight: 19.0'), 19.0)
        self.assertEqual(mock_read_weight('Weight: 23.45 grams'), 23.45)

    def test_raw_numeric(self):
        self.assertEqual(mock_read_weight('23.45'), 23.45)
        self.assertEqual(mock_read_weight('24.0g'), 24.0)
        self.assertEqual(mock_read_weight('19.0 grams'), 19.0)

    def test_invalid_input(self):
        self.assertIsNone(mock_read_weight('HX711 Ready'))
        self.assertIsNone(mock_read_weight('Calibration mode active'))

if __name__ == '__main__':
    unittest.main()
