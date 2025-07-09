#!/usr/bin/env python3
"""
Test script to demonstrate temporal extraction functionality
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from parsers.base_parser import BaseParser

# Create a test parser instance
parser = BaseParser()

# Test cases with Icelandic temporal information
test_cases = [
    {
        'text': "Hádegistilboð frá 11:00 til 15:00 á virkum dögum",
        'expected_weekdays': 'mánudagur,þriðjudagur,miðvikudagur,fimmtudagur,föstudagur',
        'expected_hours': '11:00-15:00',
        'description': 'Lunch offer from 11:00 to 15:00 on weekdays'
    },
    {
        'text': "Kvöldtilboð á föstudegi og laugardegi kl. 17:00-21:00",
        'expected_weekdays': 'föstudagur,laugardagur',
        'expected_hours': '17:00-21:00',
        'description': 'Evening offer on Friday and Saturday from 17:00-21:00'
    },
    {
        'text': "Sérstakt tilboð á sunnudegi frá 12.00 til 16.00",
        'expected_weekdays': 'sunnudagur',
        'expected_hours': '12:00-16:00',
        'description': 'Special offer on Sunday from 12.00 to 16.00'
    },
    {
        'text': "Pizza tilboð alla virka daga",
        'expected_weekdays': 'mánudagur,þriðjudagur,miðvikudagur,fimmtudagur,föstudagur',
        'expected_hours': None,
        'description': 'Pizza offer all weekdays'
    },
    {
        'text': "Helgartilboð - sérstakt verð um helgar",
        'expected_weekdays': 'laugardagur,sunnudagur',
        'expected_hours': None,
        'description': 'Weekend offer - special price on weekends'
    },
    {
        'text': "Morgun mál tilboð kl 07:00-11:00 alla daga",
        'expected_weekdays': None,
        'expected_hours': '07:00-11:00',
        'description': 'Breakfast offer 07:00-11:00 all days'
    },
    {
        'text': "Venjuleg pizza á venjulegu verði",
        'expected_weekdays': None,
        'expected_hours': None,
        'description': 'Regular pizza at regular price (no temporal info)'
    },
    {
        'text': "Tilboð frá 11 til 15 (bara númer, ekki tími)",
        'expected_weekdays': None,
        'expected_hours': None,
        'description': 'Offer from 11 to 15 (bare numbers, should not extract time)'
    }
]

def test_temporal_extraction():
    """Test the temporal extraction functionality"""
    print("🧪 TESTING TEMPORAL EXTRACTION FUNCTIONALITY")
    print("=" * 60)
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case['text']
        expected_weekdays = test_case['expected_weekdays']
        expected_hours = test_case['expected_hours']
        description = test_case['description']
        
        print(f"\n🔍 Test {i}/{total_tests}: {description}")
        print(f"   Input: '{text}'")
        
        # Extract temporal information
        weekdays, hours, availability_text = parser.extract_temporal_info(text)
        
        print(f"   Expected weekdays: {expected_weekdays}")
        print(f"   Extracted weekdays: {weekdays}")
        print(f"   Expected hours: {expected_hours}")
        print(f"   Extracted hours: {hours}")
        print(f"   Availability text: {availability_text}")
        
        # Check results
        weekdays_match = weekdays == expected_weekdays
        hours_match = hours == expected_hours
        
        if weekdays_match and hours_match:
            print("   ✅ PASS")
            passed_tests += 1
        else:
            print("   ❌ FAIL")
            if not weekdays_match:
                print(f"      Weekdays mismatch: got '{weekdays}', expected '{expected_weekdays}'")
            if not hours_match:
                print(f"      Hours mismatch: got '{hours}', expected '{expected_hours}'")
    
    print(f"\n📊 RESULTS: {passed_tests}/{total_tests} tests passed")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Temporal extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Temporal extraction needs refinement.")

if __name__ == "__main__":
    test_temporal_extraction() 