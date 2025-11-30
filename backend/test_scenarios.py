import requests
import json
import time

BASE_URL = "http://localhost:8000"

SCENARIOS = [
    {
        "name": "Trusted Source (BBC)",
        "text": """
        Scientists have discovered a new species of deep-sea jellyfish in the Pacific Ocean. 
        The findings were published in the journal Nature Marine Biology. 
        Dr. Sarah Smith, lead researcher from Oxford University, stated that this discovery changes our understanding of deep-sea ecosystems.
        The team used a remotely operated vehicle to capture high-resolution images at a depth of 4,000 meters.
        """,
        "url": "https://www.bbc.com/news/science-environment-123456"
    },
    {
        "name": "Obvious Fake News / Conspiracy",
        "text": """
        THEY DON'T WANT YOU TO KNOW! 
        Secret government documents reveal that the moon is actually a hologram projected by Big Pharma to control our minds!
        Wake up sheeple! The mainstream media won't tell you this!
        Doctors hate this one simple trick to live forever.
        Share this before it's deleted!
        """,
        "url": "https://www.conspiracy-truth-revealed.xyz/moon-fake"
    },
    {
        "name": "Clickbait / Suspicious",
        "text": """
        You won't believe what happened next! 
        This miracle cure melts fat overnight. 
        Experts are shocked by this new discovery.
        Limited time offer, act now before it's too late!
        """,
        "url": "https://viral-buzz-daily.info/shocking-news"
    }
]

def run_tests():
    print(f"Testing API at {BASE_URL}...\n")
    
    # Check Health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {resp.status_code} - {resp.json()}\n")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # Run Scenarios
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
                print(f"Status: {resp.status_code} (took {duration:.2f}s)")
                print(f"Label: {result.get('label', 'N/A').upper()}")
                print(f"Score: {result.get('score', 0):.2f}")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                print(f"Explanation: {result.get('explanation', 'N/A')}")
                print(f"Breakdown: {json.dumps(result.get('breakdown', {}), indent=2)}")
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"Request Failed: {e}")
        
        print("\n")

if __name__ == "__main__":
    run_tests()
