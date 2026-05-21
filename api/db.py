import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://szkvhvzouqvugzunvfey.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6a3ZodnpvdXF2dWd6dW52ZmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxNDY5NDEsImV4cCI6MjA5NDcyMjk0MX0.h73NOrJD8KA9tZjcaHCxHJIHjulqixAWdpCFeKa3Og8")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
