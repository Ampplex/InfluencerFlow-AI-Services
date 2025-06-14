from supabase import create_client, Client

# Replace with your Supabase project credentials
SUPABASE_URL = "https://eepxrnqcefpvzxqkpjaw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlcHhybnFjZWZwdnp4cWtwamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2MzIzNDgsImV4cCI6MjA2NDIwODM0OH0.zTsgRk2c8zdO0SnQBI9CicH_NodH_C9duSdbwojAKBQ"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample influencer data
influencer_data = {
    'id': '38497bca-0cdc-41ae-8c5c-221a3cf9f5dd',
    "influencer_username": "John Doe",
    "influencer_email": "johndoe@example.com",
    "platforms": "Instagram",
    "influencer_followers": 120000,
    "bio": "UI/UX Designer",
    'phone_num': 9325155824
}

# Insert into 'influencers' table
response = supabase.table("influencers").insert(influencer_data).execute()

# Print result
print(response.data)