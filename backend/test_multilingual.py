import requests
import json
import time

BASE_URL = "http://localhost:8000"

SCENARIOS = [
    {
        "name": "English (Trusted)",
        "text": "Scientists have discovered a new species of deep-sea jellyfish in the Pacific Ocean.",
        "url": "https://www.bbc.com/news/science-environment-123456",
        "expected_lang": "en"
    },
    {
        "name": "Spanish (Trusted - Wikipedia)",
        "text": "La Tierra gira alrededor del Sol. Es un hecho científico comprobado.",
        "url": "https://es.wikipedia.org/wiki/Tierra",
        "expected_lang": "es"
    },
    {
        "name": "French (Fake/Suspicious)",
        "text": "ILS NE VEULENT PAS QUE VOUS SACHIEZ! La lune est un hologramme!",
        "url": "https://fake-news-fr.xyz",
        "expected_lang": "fr"
    },
    {
        "name": "German (Neutral)",
        "text": "Das Wetter in Berlin ist heute sehr schön. Die Sonne scheint.",
        "url": "https://wetter.de",
        "expected_lang": "de"
    }
]

def run_tests():
    print(f"Testing Multilingual API at {BASE_URL}...\n")
    
    for scenario in SCENARIOS:
        print(f"--- Testing Scenario: {scenario['name']} ---")
        payload = {
            "text": scenario['text'],
            "url": scenario['url']
        }
        
        try:
            start_time = time.time()
            resp = requests.post(f"{BASE_URL}/analyze/text", json=payload)
            duration = time.time() - start_time
            
            if resp.status_code == 200:
                result = resp.json()
                breakdown = result.get('breakdown', {})
                detected_lang = breakdown.get('language', 'unknown')
                
                print(f"Status: {resp.status_code} (took {duration:.2f}s)")
                print(f"Detected Language: {detected_lang.upper()}")
                print(f"Label: {result.get('label', 'N/A').upper()}")
                print(f"Score: {result.get('score', 0):.2f}")
                
                if detected_lang == scenario['expected_lang']:
                    print("✅ Language Detection: PASS")
                else:
                    print(f"❌ Language Detection: FAIL (Expected {scenario['expected_lang']})")
                    
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"Request Failed: {e}")
        
        print("\n")

if __name__ == "__main__":
    run_tests()
