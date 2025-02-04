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

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t rag-chatbot .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 --env-file .env rag-chatbot
```

### Cloud Deployment

#### Heroku
```bash
heroku create
git push heroku main
heroku config:set $(cat .env)
```

#### Railway
1. Connect your GitHub repository
2. Add environment variables from .env
3. Deploy

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
