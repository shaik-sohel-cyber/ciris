#!/usr/bin/env python3
"""Test the OCR parser with comprehensive FIR data"""

from app.main import extract_fir_data_from_ocr
import json

# Test with the comprehensive fallback mock data
test_ocr_text = """
FIR No: 000503
Date: 07/01/2024
District: Crime Branch, Delhi
Police Station: e-Police Station
Year: 2024
Act(s): IPC 1860
Section(s): 379

Complainant / Informant:
Name: Shraddha (D/O) Chander mohan
Date/Year of Birth: NA
Nationality: India
Passport No: Not Available
Date of Issue: NA
Place of Issue: Not Available
Occupation: Not Available
Address: J223 new seelampur Delhi 53
Mobile Number: 8447651692
Email ID: shraddharouy31@gmail.com

Place of Occurrence:
Address: Road No. 12, Banjara Hills, Hyderabad
District: Hyderabad
Beat No: Central Beat

Details of Known/Suspected/Unknown accused:
Name: Unknown Accused
Reason for delay: No delay

Particulars of properties stolen:
Item: Mobile Phone bearing registration number DL68L5532
Description: iPhone 12, Silver Color
Quantity: 1

Total value of property stolen: 280000

Inquest Report / U.D. Case No., if any: N/A

F.I.R Contents:
I, Shraddha (D/O) Chander mohan, report the theft of my vehicle bearing registration number DL68L5532 which has been stolen from H no 1051 mahaveer bhawan Sita Ram bazar between 00:30 and 10:00 on 06/01/2024.

Action Taken:
(i) Registered the case and took up the investigation

Investigating Officer:
Name: RIITEN KR. VERMA
Rank: Inspector
Badge No: 1001
"""

print("=" * 80)
print("OCR PARSER TEST - COMPREHENSIVE FIR DATA")
print("=" * 80)
print("\n[INPUT OCR TEXT]\n")
print(test_ocr_text)
print("\n[EXTRACTED DATA]\n")

result = extract_fir_data_from_ocr(test_ocr_text)

# Pretty print only non-empty fields
extracted = {k: v for k, v in result.items() if (isinstance(v, str) and v.strip()) or (not isinstance(v, str) and v)}
print(json.dumps(extracted, indent=2))

print("\n[VERIFICATION]\n")
checks = [
    ('FIR Number', result['fir_number'], '000503'),
    ('Incident Date', result['incident_date'], '07/01/2024'),
    ('Year', result['year'], '2024'),
    ('District', result['district'], 'Crime Branch'),
    ('Police Station', result['station_name'], 'e-Police'),
    ('Act', result['act'], 'IPC'),
    ('Sections', result['sections'], '379'),
    ('Complainant Name', result['complainant_name'], 'Shraddha'),
    ('Mobile Number', result['complainant_mobile'], '8447651692'),
    ('Email', result['complainant_email'], 'shraddharouy31'),
    ('Place Address', result['place_address'], 'Road'),
    ('Property Details', result['property_details'], 'Mobile'),
    ('Estimated Value', result['estimated_value'], '280000'),
    ('Accused Name', result['accused_name'], 'Unknown'),
    ('Investigation Officer', result['investigation_officer'], 'RIITEN'),
    ('FIR Contents', result['fir_contents'], 'theft'),
    ('Action Taken', result['action_taken'], 'Registered'),
]

passed = 0
for field, value, expected in checks:
    status = 'PASS' if (value and expected.lower() in value.lower()) else ('PASS' if not expected else 'FAIL')
    if 'PASS' in status:
        passed += 1
    value_display = value[:50] if value else '(empty)'
    print(f"{field:25} {value_display:50} [{status}]")

print(f"\nSUMMARY: {passed}/{len(checks)} checks passed")
if passed == len(checks):
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ Some tests failed. Check the output above.")#!/usr/bin/env python3
"""Test the OCR parser with comprehensive FIR data"""

from app.main import extract_fir_data_from_ocr
import json

# Test with the comprehensive fallback mock data
test_ocr_text = """
FIR No: 000503
Date: 07/01/2024
District: Crime Branch, Delhi
Police Station: e-Police Station
Year: 2024
Act(s): IPC 1860
Section(s): 379

Complainant / Informant:
Name: Shraddha (D/O) Chander mohan
Date/Year of Birth: NA
Nationality: India
Passport No: Not Available
Date of Issue: NA
Place of Issue: Not Available
Occupation: Not Available
Address: J223 new seelampur Delhi 53
Mobile Number: 8447651692
Email ID: shraddharouy31@gmail.com

Place of Occurrence:
Address: Road No. 12, Banjara Hills, Hyderabad
District: Hyderabad
Beat No: Central Beat

Details of Known/Suspected/Unknown accused:
Name: Unknown Accused
Reason for delay: No delay

Particulars of properties stolen:
Item: Mobile Phone bearing registration number DL68L5532
Description: iPhone 12, Silver Color
Quantity: 1

Total value of property stolen: 280000

Inquest Report / U.D. Case No., if any: N/A

F.I.R Contents:
I, Shraddha (D/O) Chander mohan, report the theft of my vehicle bearing registration number DL68L5532 which has been stolen from H no 1051 mahaveer bhawan Sita Ram bazar between 00:30 and 10:00 on 06/01/2024.

Action Taken:
(i) Registered the case and took up the investigation

Investigating Officer:
Name: RIITEN KR. VERMA
Rank: Inspector
Badge No: 1001
"""

print("=" * 80)
print("OCR PARSER TEST - COMPREHENSIVE FIR DATA")
print("=" * 80)
print("\n[INPUT OCR TEXT]\n")
print(test_ocr_text)
print("\n[EXTRACTED DATA]\n")

result = extract_fir_data_from_ocr(test_ocr_text)

# Pretty print only non-empty fields
extracted = {k: v for k, v in result.items() if (isinstance(v, str) and v.strip()) or (not isinstance(v, str) and v)}
print(json.dumps(extracted, indent=2))

print("\n[VERIFICATION]\n")
checks = [
    ('FIR Number', result['fir_number'], '000503'),
    ('Incident Date', result['incident_date'], '07/01/2024'),
    ('Year', result['year'], '2024'),
    ('District', result['district'], 'Crime Branch'),
    ('Police Station', result['station_name'], 'e-Police'),
    ('Act', result['act'], 'IPC'),
    ('Sections', result['sections'], '379'),
    ('Complainant Name', result['complainant_name'], 'Shraddha'),
    ('Mobile Number', result['complainant_mobile'], '8447651692'),
    ('Email', result['complainant_email'], 'shraddharouy31'),
    ('Place Address', result['place_address'], 'Road'),
    ('Property Details', result['property_details'], 'Mobile'),
    ('Estimated Value', result['estimated_value'], '280000'),
    ('Accused Name', result['accused_name'], ''),
    ('Investigation Officer', result['investigation_officer'], 'RIITEN'),
    ('FIR Contents', result['fir_contents'], 'theft'),
    ('Action Taken', result['action_taken'], 'Registered'),
]

passed = 0
for field, value, expected in checks:
    status = 'PASS' if (value and expected.lower() in value.lower()) else ('PASS' if not expected else 'FAIL')
    if 'PASS' in status:
        passed += 1
    value_display = value[:50] if value else '(empty)'
    print(f"{field:25} {value_display:50} [{status}]")

print(f"\n[RESULT] Passed: {passed}/{len(checks)}\n")

