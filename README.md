# FlirtGPT

A small character-level GPT chat app powered by the existing V1 checkpoint at `flirtgpt.pt`. The app uses the model and character vocabulary saved in that checkpoint; it does not retrain the model or call an external language model.

## Run locally

Start the API in one terminal:

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Start the React app in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at <http://localhost:5173>. The API listens at <http://localhost:8000>; its health endpoint is <http://localhost:8000/api/health>.

The backend resolves `flirtgpt.pt` from the repository root and loads it once at startup. It selects CUDA when available and otherwise CPU. Set `FLIRTGPT_CORS_ORIGINS` to a comma-separated list of allowed origins for a deployment. Set `VITE_API_URL` in the frontend environment if the API is hosted somewhere other than `http://localhost:8000`.

## Notes

- `backend/model.py` mirrors the V1 `GPTLanguageModel` architecture and consumes the checkpoint's saved dimensions and `chars` vocabulary.
- `backend/main.py` provides `GET /api/health` and `POST /api/chat`.
- Conversation history is held in the browser for the current chat. “New chat” clears it.
- Backend request validation limits each message to 2,000 characters and history to 40 messages.
