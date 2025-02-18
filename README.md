# RAG Chatbot with Multiple LLM Providers

A Retrieval-Augmented Generation (RAG) chatbot system that allows users to upload documents and chat with them using various LLM providers.

## Features

- Multiple LLM Provider Support (Mistral, Deepseek, Groq, Cohere)
- Document Upload and Processing
- Vector Storage with Pinecone
- User Authentication with JWT
- Role-based Access Control (Admin/User)
- Chat History Management
- Session Management

## Prerequisites

- Python 3.9+
- Pinecone Account
- Supabase Account
- One or more of the following API keys:
  - HuggingFace API key (for Mistral/Deepseek)
  - Groq API key
  - Cohere API key

## Supabase Setup

1. **Create Supabase Project:**
   - Go to https://supabase.com/
   - Create a new project
   - Note your project URL and anon/public API key

2. **Create Storage Bucket:**
   ```sql
   -- In Supabase SQL Editor
   insert into storage.buckets (id, name)
   values ('documents', 'documents');
   ```

3. **Create Documents Table:**
   ```sql
   create table public.documents (
     id uuid primary key,
     filename text not null,
     uploader_email text not null,
     pinecone_namespace text,
     upload_date timestamp with time zone default now(),
     file_type text not null,
     status text default 'active',
     page_count integer,
     file_size integer,
     created_at timestamp with time zone default now()
   );

   -- Add RLS policies
   alter table public.documents enable row level security;

   -- Allow users to see their own documents
   create policy "Users can view their own documents"
     on documents for select
     using (uploader_email = auth.jwt() ->> 'email');

   -- Allow users to upload documents
   create policy "Users can upload documents"
     on documents for insert
     with check (uploader_email = auth.jwt() ->> 'email');
   ```

4. **Storage Policies:**
   ```sql
   -- Allow read access to authenticated users
   create policy "Allow authenticated read access"
     on storage.objects for select
     using (auth.role() = 'authenticated');

   -- Allow uploads to authenticated users
   create policy "Allow authenticated uploads"
     on storage.objects for insert
     with check (auth.role() = 'authenticated');
   ```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

2. Install system dependencies:

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install libmagic1

# On macOS
brew install libmagic

# On Windows
# No additional steps needed - magic patterns included in python-magic
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory:
```env
# Vector DB
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=arya-embeddings
PINECONE_HOST=your_pinecone_host

# Auth
JWT_SECRET_KEY=your_secret_key

# LLM Providers
HUGGINGFACE_API_KEY=your_huggingface_key
GROQ_API_KEY=your_groq_key
COHERE_API_KEY=your_cohere_key

# Current LLM Provider
LLM_PROVIDER=mistral

# Document Storage
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

6. Initialize Pinecone:
   - Create a Pinecone account
   - Create an index with dimension 768 (for default embeddings)
   - Update the index name in `backend/utils.py`

## Pinecone Setup

1. **Create Pinecone Account:**
   - Go to https://app.pinecone.io/
   - Sign up for a free account

2. **Find Your Environment Details:**
   - In Pinecone Console, click on your index "arya-embeddings"
   - Note the following details:
     - Cloud: AWS
     - Region: us-east-1
     - Host: Your full host URL (ends with .pinecone.io)

3. **Create Index:**
   ```bash
   # Index Configuration
   Name: arya-embeddings (or your preferred name)
   Dimensions: 768 (for sentence-transformers embeddings)
   Metric: cosine
   ```
   Steps:
   - Click "Create Index" in Pinecone Console
   - Enter "arya-embeddings" as the index name
   - Set Dimensions to 768
   - Choose "cosine" as the metric
   - Select "gcp-starter" as the environment
   - Click "Create Index"

3. **Get Environment Details:**
   - After creating the index, note your environment:
     - For free tier: Usually `gcp-starter` or `asia-southeast1-gcp-free`
     - You can find this in the Pinecone console under "API Keys"

4. **Update .env file:**
   ```env
   PINECONE_API_KEY=your_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=arya-embeddings
   ```

4. **Verify Connection:**
   ```python
   # Save as check_pinecone.py
   import os
   import pinecone
   from dotenv import load_dotenv

   load_dotenv()

   # Initialize Pinecone with correct environment
   pinecone.init(
       api_key=os.getenv("PINECONE_API_KEY"),
       environment="us-east-1"  # AWS region
   )

   # Should show "arya-embeddings"
   print("Available indexes:", pinecone.list_indexes())

   # Get index details
   index = pinecone.Index("arya-embeddings")
   print("\nIndex description:", index.describe_index_stats())
   ```

> Note: The environment value should match your AWS region (us-east-1) rather than the previously mentioned gcp-starter.

## Running the Application

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
streamlit run app.py
```

3. Access the application:
   - Frontend: http://localhost:8501
   - API docs: http://localhost:8000/docs

## Default Users

- Admin:
  - Username: admin
  - Password: adminpassword
- Regular User:
  - Username: user
  - Password: userpassword

## Deployment

### Frontend (Streamlit Community Cloud)

1. **Prepare Your Repository:**
   - Ensure your code is in a GitHub repository
   - Repository structure should be:
   ```
   ├── frontend/
   │   ├── app.py          # Streamlit application
   │   └── requirements.txt # Frontend dependencies
   ├── backend/
   │   └── ...            # Backend files
   └── requirements.txt    # Main requirements
   ```

2. **Create Streamlit Account:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"

3. **Deploy Settings:**
   ```
   Repository: your-github-username/rag-chatbot
   Branch: main
   Main file path: frontend/app.py
   Python version: 3.9
   ```

4. **Environment Variables:**
   - In Streamlit Cloud, go to "Advanced settings"
   - Add the following secrets in the "Secrets" field:
   ```toml
   [env]
   BACKEND_URL = "your-backend-url"  # e.g., "https://your-backend.onrender.com"
   
   # Vector DB
   PINECONE_API_KEY = "your-pinecone-key"
   PINECONE_ENVIRONMENT = "us-east-1"
   PINECONE_INDEX_NAME = "arya-embeddings"
   PINECONE_HOST = "your-pinecone-host"
   
   # Auth
   JWT_SECRET_KEY = "your-jwt-secret"
   
   # LLM Providers
   HUGGINGFACE_API_KEY = "your-huggingface-key"
   GROQ_API_KEY = "your-groq-key"
   COHERE_API_KEY = "your-cohere-key"
   
   # Current LLM Provider
   LLM_PROVIDER = "mistral"
   
   # Document Storage
   SUPABASE_URL = "your-project-url"
   SUPABASE_KEY = "your-anon-key"
   ```

5. **Frontend Requirements:**
   Create `frontend/requirements.txt`:
   ```text
   streamlit>=1.24.0
   requests>=2.28.2
   python-jose[cryptography]>=3.3.0
   ```

6. **Deploy:**
   - Click "Deploy!"
   - Wait for the build to complete
   - Your app will be available at `https://share.streamlit.io/your-username/rag-chatbot`

7. **Troubleshooting:**
   - Check "Manage app" → "Logs" for any issues
   - Ensure all environment variables are set correctly
   - Verify the backend URL is accessible from Streamlit Cloud
   - Check that the Python version matches your requirements

> Note: Make sure your backend is deployed and accessible before deploying the frontend, as Streamlit will need to communicate with it.

### Updating the Deployment

1. **Push Changes:**
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```

2. **Redeployment:**
   - Streamlit Cloud automatically redeploys when you push to the main branch
   - You can also manually trigger a redeployment from the Streamlit Cloud dashboard

3. **Monitor:**
   - Watch the deployment logs for any errors
   - Test the application after each deployment
   - Check that environment variables are still properly set

### Backend (Free Options)

1. **Railway** (Free tier available):
   - 500 hours free per month
   - 512MB RAM
   - Setup:
   ```bash
   # Deploy only the backend directory
   git subtree push --prefix backend railway main
   ```

2. **Render** (Free tier):
   - Free tier includes:
   - 750 hours free per month
   - Automatic HTTPS
   - Setup:
   ```bash
   # Create render.yaml
   services:
     - type: web
       name: rag-chatbot-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
   ```

3. **Fly.io** (Free tier):
   - 3 shared-cpu-1x 256mb VMs
   - 3GB persistent volume storage
   - Setup:
   ```bash
   # Install flyctl
   curl -L https://fly.io/install.sh | sh
   
   # Deploy
   fly launch
   fly secrets set < .env
   fly deploy
   ```

### Cost-Saving Tips

1. **LLM Provider Selection:**
   - Use Mistral with HuggingFace (free tier available)
   - Groq offers free credits for new users
   - Cohere has a generous free tier

2. **Vector Database:**
   - Pinecone's free tier includes:
     - 1 project
     - 1 index
     - 10,000 vectors
     - 100 queries per second

3. **Scaling Considerations:**
   - Start with the Mistral provider (most cost-effective)
   - Use smaller chunk sizes for documents
   - Implement caching for frequent queries
   - Monitor usage to stay within free tiers

4. **Development Tips:**
   - Use local development with smaller test files
   - Implement rate limiting
   - Cache responses when possible
   - Monitor API usage carefully

> Note: Remember to check the current pricing and limitations of each service as they may change over time.

## API Endpoints

- `POST /token` - Login and get access token
- `POST /upload` - Upload document (admin only)
- `POST /chat/{session_id}` - Chat with documents
- `GET /chat/sessions` - Get user's chat sessions
- `GET /chat/{session_id}/history` - Get chat history
- `POST /config/llm-provider` - Change LLM provider (admin only)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Security and API Keys Setup

1. **Required API Keys:**

   a) **Pinecone:**
   - Go to https://app.pinecone.io/
   - Sign up for a free account
   - Click "API Keys" in the left sidebar
   - Copy your API key and environment details

   b) **HuggingFace:**
   - Go to https://huggingface.co/
   - Create an account or sign in
   - Visit https://huggingface.co/settings/tokens
   - Click "New token"
   - Give it a name (e.g., "rag-chatbot")
   - Select "read" access
   - Copy the generated token

   c) **Groq (Optional):**
   - Visit https://console.groq.com/
   - Sign up for an account
   - Click on "API Keys" in the dashboard
   - Click "Create API Key"
   - Give it a name (e.g., "rag-chatbot")
   - Copy the API key (starts with "gsk_")
   - Note: New users get free credits

   d) **Cohere (Optional):**
   - Go to https://dashboard.cohere.com/
   - Create an account
   - Navigate to https://dashboard.cohere.com/api-keys
   - Click "Create API Key"
   - Select "Trial" access
   - Name your key (e.g., "rag-chatbot")
   - Copy the generated key
   - Note: Free tier includes 5M tokens/month

2. **Generate JWT Secret:**
```bash
# On Linux/Mac
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

3. **Local Development:**
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Add your keys to `.env`:
   ```env
   # Vector DB
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=arya-embeddings
   PINECONE_HOST=your_pinecone_host

   # Auth
   JWT_SECRET_KEY=generated_secret

   # LLM Providers
   HUGGINGFACE_API_KEY=your_huggingface_key  # Required for Mistral
   GROQ_API_KEY=your_groq_key                # Optional
   COHERE_API_KEY=your_cohere_key           # Optional

   # Current LLM Provider
   LLM_PROVIDER=mistral
   ```

4. **Verify API Keys:**
```python
# Save as test_api_keys.py
import os
from dotenv import load_dotenv
from llm_config import get_llm, LLMProvider

load_dotenv()

def test_key(provider: str, env_var: str):
    key = os.getenv(env_var)
    print(f"\n{provider} API Key:")
    print(f"- Present: {bool(key)}")
    print(f"- Length: {len(key) if key else 0}")
    print(f"- Format: {'Valid' if key and len(key) > 20 else 'Invalid'}")

# Test each provider
test_key("HuggingFace", "HUGGINGFACE_API_KEY")
test_key("Groq", "GROQ_API_KEY")
test_key("Cohere", "COHERE_API_KEY")
```

5. **API Key Usage Limits:**

   - **HuggingFace:**
     - Free tier: Rate limited
     - Recommended for development

   - **Groq:**
     - Free credits for new users
     - Pay-as-you-go after credits
     - Fast inference speeds

   - **Cohere:**
     - 5M tokens/month free
     - Rate limits apply
     - Good for production use

> ⚠️ **Security Note**: Never commit API keys or secrets to version control. Always use environment variables or secure secrets management in production.

## Testing the Application

1. **Environment Setup Test**
```bash
# Check if environment variables are loaded
python -c "import os; print('PINECONE_API_KEY:', bool(os.getenv('PINECONE_API_KEY')))"
python -c "import os; print('JWT_SECRET_KEY:', bool(os.getenv('JWT_SECRET_KEY')))"
```

2. **Backend API Tests**
```bash
# Start the backend
cd backend
uvicorn main:app --reload --port 8000

# In another terminal, test the endpoints:

# 1. Login as admin
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpassword"

# Save the token
export TOKEN="your_access_token_here"

# 2. Upload a test document
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"

# 3. Create a chat session
curl -X POST "http://localhost:8000/chat/session" \
  -H "Authorization: Bearer $TOKEN"

# Save the session ID
export SESSION_ID="your_session_id_here"

# 4. Test chat
curl -X POST "http://localhost:8000/chat/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is in the document?"}'
```

3. **Frontend Test**
```bash
# Start the frontend
cd frontend
streamlit run app.py

# Then open http://localhost:8501 and:
1. Log in with admin/adminpassword
2. Upload a test document
3. Create a new chat session
4. Try asking questions about the document
```

4. **Create a Test Document**
```bash
# Create a test.txt file
echo "This is a test document. It contains information about testing." > test.txt
```

5. **LLM Provider Test**
```python
# Create test_llm.py
from llm_config import get_llm, LLMProvider
import os

# Test each provider
providers = [LLMProvider.MISTRAL, LLMProvider.GROQ, LLMProvider.COHERE]

for provider in providers:
    try:
        llm = get_llm(provider)
        response = llm("Say hello!")
        print(f"{provider}: {response}")
    except Exception as e:
        print(f"{provider} failed: {str(e)}")
```

6. **Troubleshooting**

If you encounter issues:

- Check logs:
```bash
tail -f backend/app.log
```

- Verify Pinecone connection:
```python
import pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), 
              environment=os.getenv("PINECONE_ENVIRONMENT"))
print(pinecone.list_indexes())
```

- Test JWT token:
```python
from auth import create_access_token
token = create_access_token(data={"sub": "test"})
print("Token generated:", bool(token))
```

- Check session storage:
```bash
cat data/sessions.json
```

Common Issues:
- 401 Unauthorized: Check your JWT token
- 403 Forbidden: Verify you're using an admin account for restricted endpoints
- 500 Server Error: Check the logs for details
- Connection Error: Verify your API keys and network connection

### Troubleshooting Supabase

1. **Storage Issues:**
   - Check bucket permissions in Supabase dashboard
   - Verify RLS policies are correctly set
   - Ensure file size is within limits

2. **Database Issues:**
   - Check table structure matches Document model
   - Verify RLS policies allow intended operations
   - Monitor storage usage in Supabase dashboard

3. **Common Errors:**
   - 403: Check authentication and RLS policies
   - 413: File size too large
   - Storage not found: Verify bucket exists

### Troubleshooting

#### Python-magic Issues:

1. **Linux/macOS:**
   ```bash
   # If you see "ImportError: failed to find libmagic"
   # Ubuntu/Debian:
   sudo apt-get install libmagic1
   
   # macOS:
   brew install libmagic
   ```

2. **Windows:**
   - python-magic includes magic patterns, no additional setup needed
   - If you encounter issues, try:
     ```bash
     pip uninstall python-magic
     pip install python-magic-bin  # Windows-specific alternative
     ```

Common Issues:
- 401 Unauthorized: Check your JWT token
