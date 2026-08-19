import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL found:", bool(url))
print("KEY found:", bool(key))

supabase = create_client(url, key)

response = supabase.table("generations").select("*").execute()

print("✅ SUPABASE CONNECTED!")
print("Database records:", response.data)