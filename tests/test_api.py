"""
API Testing Examples
Run with: python test_api.py
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_text_analysis():
    """Test text analysis endpoint"""
    print("\n=== Testing Text Analysis ===")
    
    # Example 1: Trustworthy text
    text1 = """
    According to a study published in Nature journal, researchers at MIT have developed 
    a new method for carbon capture that could reduce atmospheric CO2 levels. The peer-reviewed 
    research was conducted over three years with multiple validation studies.
    """
    
    response = requests.post(
        f"{API_BASE_URL}/analyze/text",
        json={"text": text1}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Example 2: Suspicious text
    text2 = """
    SHOCKING discovery! Scientists don't want you to know this secret miracle cure 
    that will change everything! Click here now before it's too late! This exclusive 
    leaked information will blow your mind!
    """
    
    response = requests.post(
        f"{API_BASE_URL}/analyze/text",
        json={"text": text2}
    )
    print(f"\nSuspicious Text Analysis:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_image_analysis():
    """Test image analysis endpoint"""
    print("\n=== Testing Image Analysis ===")
    
    # Example image URL
    image_url = "https://picsum.photos/800/600"
    
    response = requests.post(
        f"{API_BASE_URL}/analyze/image",
        json={"image_url": image_url}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_audio_analysis():
    """Test audio analysis endpoint"""
    print("\n=== Testing Audio Analysis ===")
    
    # Example audio URL (would need real audio file)
    audio_url = "https://example.com/sample.mp3"
    
    response = requests.post(
        f"{API_BASE_URL}/analyze/audio",
        json={"audio_url": audio_url}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_report():
    """Test report retrieval"""
    print("\n=== Testing Report Retrieval ===")
    
    # First create a report
    text = "Sample text for testing report retrieval"
    response = requests.post(
        f"{API_BASE_URL}/analyze/text",
        json={"text": text}
    )
    
    if response.status_code == 200:
        report_id = response.json()['report_id']
        print(f"Created report: {report_id}")
        
        # Now retrieve it
        report_response = requests.get(f"{API_BASE_URL}/report/{report_id}")
        print(f"Status: {report_response.status_code}")
        print(f"Response: {json.dumps(report_response.json(), indent=2)}")

if __name__ == "__main__":
    print("RealityFix API Testing")
    print("=" * 50)
    
    try:
        test_health()
        test_text_analysis()
        test_image_analysis()
        # test_audio_analysis()  # Uncomment when audio URL is available
        test_get_report()
        
        print("\n" + "=" * 50)
        print("Testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API.")
        print("Make sure the backend is running: python backend/app.py")
    except Exception as e:
        print(f"\nError during testing: {e}")