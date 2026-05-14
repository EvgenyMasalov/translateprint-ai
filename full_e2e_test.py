import urllib.request
import json
import time

def test_e2e():
    base_url = "http://127.0.0.1:5678"
    email = f"e2e_{int(time.time())}@test.com"
    password = "password123"

    print(f"Testing with email: {email}")

    # 1. Register
    reg_data = json.dumps({
        "first_name": "E2E",
        "last_name": "Test",
        "email": email,
        "password": password
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/register", data=reg_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        reg_res = json.loads(res.read().decode('utf-8'))
        token = reg_res['access_token']
        print("Registration: OK")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }

    # 2. Get Profile
    req = urllib.request.Request(f"{base_url}/me", headers=headers)
    with urllib.request.urlopen(req) as res:
        profile = json.loads(res.read().decode('utf-8'))
        print(f"Profile: OK (User: {profile['email']})")

    # 3. Create Song
    song_data = json.dumps({
        "title": "E2E Song",
        "lyrics": "This is a test song for E2E validation."
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/songs", data=song_data, headers=headers)
    with urllib.request.urlopen(req) as res:
        song = json.loads(res.read().decode('utf-8'))
        song_id = song['id']
        print(f"Create Song: OK (ID: {song_id})")

    # 4. List Songs
    req = urllib.request.Request(f"{base_url}/songs", headers=headers)
    with urllib.request.urlopen(req) as res:
        songs = json.loads(res.read().decode('utf-8'))
        print(f"List Songs: OK (Count: {len(songs)})")

    # 5. Analyze Lyrics (Mock)
    # We need to set mock URL in .env or assume it's working
    # Let's try to call it and see if it fails with 502 (expected if no real n8n) or succeeds (if mock)
    analyze_data = json.dumps({
        "chatInput": "Test lyrics",
        "targetLanguage": "Russian"
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/webhook/analyze-lyrics", data=analyze_data, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            analysis = json.loads(res.read().decode('utf-8'))
            print("Analyze Lyrics: OK (Mock or Real)")
    except urllib.error.HTTPError as e:
        print(f"Analyze Lyrics: Failed with {e.code} (Expected if no n8n)")

if __name__ == "__main__":
    test_e2e()
