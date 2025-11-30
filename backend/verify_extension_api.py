import requests
import json
import sys

def test_api():
    url = "http://localhost:8000/analyze/text"
    payload = {
        "text": "This is a test sentence to verify the Reality Fix extension API is working correctly.",
        "url": "http://example.com"
    }
    
    print(f"Testing API endpoint: {url}")
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Response Received:")
            print(json.dumps(data, indent=2))
            
            # Verify expected fields for extension
            required_fields = ['score', 'label', 'explanation', 'confidence']
            missing = [f for f in required_fields if f not in data]
            
            if not missing:
                print("\n✅ Response structure is valid for Extension")
                return True
            else:
                print(f"\n❌ Missing fields required by extension: {missing}")
                return False
        else:
            print(f"\n❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        print("Is the backend server running?")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
