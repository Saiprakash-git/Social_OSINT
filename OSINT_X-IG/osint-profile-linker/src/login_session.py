import instaloader

USERNAME = "insta_user_osint"
PASSWORD = "1234567890."

L = instaloader.Instaloader()

try:
    L.login(USERNAME, PASSWORD)
    L.save_session_to_file()
    print("✅ Session saved successfully as", USERNAME + ".session")
except Exception as e:
    print("❌ Login failed:", e)
