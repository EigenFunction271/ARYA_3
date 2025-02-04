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
- One or more of the following API keys:
  - HuggingFace API key (for Mistral/Deepseek)
  - Groq API key
  - Cohere API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
# Vector DB
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment

# Auth
JWT_SECRET_KEY=your_secret_key

# LLM Providers (add the ones you plan to use)
HUGGINGFACE_API_KEY=your_huggingface_key
GROQ_API_KEY=your_groq_key
COHERE_API_KEY=your_cohere_key

# Current LLM Provider
LLM_PROVIDER=mistral  # Options: mistral, deepseek, groq, cohere
```

5. Initialize Pinecone:
   - Create a Pinecone account
   - Create an index with dimension 768 (for default embeddings)
   - Update the index name in `backend/utils.py`

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

### Frontend (Free Options)

1. **Streamlit Community Cloud** (Recommended):
   - Sign up at https://share.streamlit.io/
   - Connect your GitHub repository
   - Select the `frontend/app.py` file
   - Add your environment variables in Streamlit's secrets management
   - Deploy (automatically updates with your repository)

2. **GitHub Pages** (Alternative):
   - Create a static build of the Streamlit app:
   ```bash
   cd frontend
   streamlit run app.py --browser.serverAddress="0.0.0.0" --server.port=8501 --server.address="0.0.0.0"
   ```
   - Enable GitHub Pages in your repository settings
   - Deploy the static files to the `gh-pages` branch

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
   - Pinecone: Sign up at https://www.pinecone.io/
   - HuggingFace: Get API key at https://huggingface.co/settings/tokens
   - Groq (Optional): Sign up at https://console.groq.com/
   - Cohere (Optional): Get API key at https://dashboard.cohere.com/api-keys

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
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_environment
   JWT_SECRET_KEY=generated_secret
   HUGGINGFACE_API_KEY=your_huggingface_key
   GROQ_API_KEY=your_groq_key
   COHERE_API_KEY=your_cohere_key
   ```

4. **Production Deployment:**
   - Never commit `.env` file
   - Set environment variables in your deployment platform
   - For Docker: Use `--env-file` or environment variables
   - For Heroku/Railway: Use platform's secrets management

5. **Verify Security:**
```bash
# Check if .env is ignored
git check-ignore .env

# Check for sensitive files before committing
git status
```

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
