#!/usr/bin/env python3
"""
Update weight values in Thompson-Alananah.sql vitals section

Alananah's weight trajectory (female, 65" height):
- 2010-2011: 145-150 lbs (BMI 24-25, healthy post-military)
- 2012-2013: 135-145 lbs (weight loss during breast cancer treatment/chemo)
- 2014-2019: 155-175 lbs (gradual gain, BMI 26-29, overweight)
- 2020-2025: 185-195 lbs (BMI 31-33, obesity, diabetes management)

Bailey's trajectory (male, 70" height): 185 → 245 → 220 lbs
"""

import re
from pathlib import Path

script_file = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Thompson-Alananah.sql")

def calculate_female_weights():
    """
    Generate realistic weight progression for Alananah over 15 years
    Returns dict mapping year-quarter to weight in lbs
    """
    weights = {}

    # 2010: Baseline (145-148 lbs)
    weights['2010-Q2'] = 148  # Jun
    weights['2010-Q3'] = 147  # Sep
    weights['2010-Q4'] = 146  # Dec

    # 2011: Stable (145-148 lbs)
    weights['2011-Q1'] = 145  # Mar
    weights['2011-Q2'] = 146  # Jun
    weights['2011-Q3'] = 147  # Sep
    weights['2011-Q4'] = 148  # Dec

    # 2012: Diabetes diagnosis + cancer treatment (135-145 lbs, weight loss)
    weights['2012-Q1'] = 150  # Mar (pre-diagnosis)
    weights['2012-Q2'] = 145  # Jun (diabetes diagnosis)
    weights['2012-Q3'] = 138  # Sep (chemo weight loss)
    weights['2012-Q4'] = 135  # Dec (lowest weight during treatment)

    # 2013: Cancer recovery (135-145 lbs, gradual regain)
    weights['2013-Q1'] = 137  # Mar
    weights['2013-Q2'] = 140  # Jun
    weights['2013-Q3'] = 143  # Sep
    weights['2013-Q4'] = 145  # Dec

    # 2014-2015: Gradual weight gain (145-160 lbs)
    weights['2014-Q1'] = 147
    weights['2014-Q2'] = 150
    weights['2014-Q3'] = 153
    weights['2014-Q4'] = 155
    weights['2015-Q1'] = 158
    weights['2015-Q2'] = 160
    weights['2015-Q3'] = 162
    weights['2015-Q4'] = 164

    # 2016-2017: Continued gain (165-172 lbs)
    weights['2016-Q1'] = 165
    weights['2016-Q2'] = 167
    weights['2016-Q3'] = 168
    weights['2016-Q4'] = 170
    weights['2017-Q1'] = 171
    weights['2017-Q2'] = 172
    weights['2017-Q3'] = 173
    weights['2017-Q4'] = 174

    # 2018-2019: Peak weight (175-180 lbs)
    weights['2018-Q1'] = 175
    weights['2018-Q2'] = 177
    weights['2018-Q3'] = 178
    weights['2018-Q4'] = 179
    weights['2019-Q1'] = 180
    weights['2019-Q2'] = 181
    weights['2019-Q3'] = 182
    weights['2019-Q4'] = 183

    # 2020-2021: Diabetes complications, further gain (184-190 lbs)
    weights['2020-Q1'] = 184
    weights['2020-Q2'] = 186
    weights['2020-Q3'] = 187
    weights['2020-Q4'] = 188
    weights['2021-Q1'] = 189
    weights['2021-Q2'] = 190
    weights['2021-Q3'] = 191
    weights['2021-Q4'] = 192

    # 2022-2025: Stable obesity (190-195 lbs)
    weights['2022-Q1'] = 193
    weights['2022-Q2'] = 194
    weights['2022-Q3'] = 193
    weights['2022-Q4'] = 192
    weights['2023-Q1'] = 191
    weights['2023-Q2'] = 192
    weights['2023-Q3'] = 193
    weights['2023-Q4'] = 194
    weights['2024-Q1'] = 194
    weights['2024-Q2'] = 195
    weights['2024-Q3'] = 194
    weights['2024-Q4'] = 193
    weights['2025-Q1'] = 192

    return weights

def get_quarter(month):
    """Convert month to quarter"""
    if month in ['01', '02', '03']: return 'Q1'
    elif month in ['04', '05', '06']: return 'Q2'
    elif month in ['07', '08', '09']: return 'Q3'
    else: return 'Q4'

def lbs_to_kg(lbs):
    """Convert pounds to kilograms"""
    return round(lbs * 0.453592, 1)

def main():
    print("=" * 70)
    print("Updating Weight Values in Thompson-Alananah.sql Vitals")
    print("=" * 70)

    # Read file
    print("\n1. Reading Thompson-Alananah.sql...")
    content = script_file.read_text()

    # Generate weight mapping
    print("\n2. Generating female weight trajectory...")
    weights = calculate_female_weights()
    print(f"   Generated {len(weights)} quarterly weight values")
    print(f"   Range: {min(weights.values())} - {max(weights.values())} lbs")

    # Find all weight entries in vitals (VitalTypeSID 6 = Weight)
    print("\n3. Finding and updating weight values...")

    # Pattern to match weight vital entries with dates
    # Example: (10002, 2002, 6, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '185', 185, NULL, NULL, 84.0,
    # VitalSignSID for Alananah: 10001-10231 (5 digits)
    pattern = r"\((\d{5}), 2002, 6, '(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}', '(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}', '\d+', \d+, NULL, NULL, \d+\.?\d*,"

    matches = list(re.finditer(pattern, content))
    print(f"   Found {len(matches)} weight entries to update")

    updates = 0
    for match in matches:
        vital_sid = match.group(1)
        year = match.group(2)
        month = match.group(3)
        quarter = get_quarter(month)

        # Look up weight for this year-quarter
        key = f"{year}-{quarter}"
        if key in weights:
            new_weight_lbs = weights[key]
            new_weight_kg = lbs_to_kg(new_weight_lbs)

            # Replace the entire VALUES row
            old_row = match.group(0)
            new_row = old_row.replace(
                f"'{match.group(5)}-{match.group(6)}-{match.group(7)} ",
                f"'{match.group(5)}-{match.group(6)}-{match.group(7)} "
            )
            # Extract and replace weight values
            parts = old_row.split(", ")
            # parts[5] is the string value, parts[6] is numeric, parts[9] is metric
            parts[5] = f"'{new_weight_lbs}'"
            parts[6] = str(new_weight_lbs)
            parts[9] = f"{new_weight_kg},"

            new_row = ", ".join(parts)
            content = content.replace(old_row, new_row)
            updates += 1

            if updates <= 5:  # Show first 5 updates
                print(f"      {year}-{month} ({quarter}): → {new_weight_lbs} lbs ({new_weight_kg} kg)")

    print(f"   ✓ Updated {updates} weight entries")

    # Write updated content
    print("\n4. Writing updated Thompson-Alananah.sql...")
    script_file.write_text(content)
    print(f"   ✓ File updated: {script_file}")

    print("\n" + "=" * 70)
    print("✅ Weight values updated successfully!")
    print("=" * 70)
    print("\nWeight trajectory:")
    print("  2010-2011: 145-150 lbs (BMI 24-25, healthy)")
    print("  2012-2013: 135-145 lbs (cancer treatment weight loss)")
    print("  2014-2019: 155-183 lbs (gradual gain, overweight)")
    print("  2020-2025: 184-195 lbs (obesity, diabetes management)")

if __name__ == "__main__":
    main()
