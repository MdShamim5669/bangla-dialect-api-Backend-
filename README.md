# Bangla Regional Dialect Translator — Backend API

RESTful API backend for translating 7 regional dialects of Bangladesh (*Chittagong, Noakhali, Barishal, Rangpur, Pabna, Mymensingh, Jashore*) into Standard Bengali using the fine-tuned `BanglaT5` model architecture.

---

## 🌟 Key Features
- **FastAPI Service**: High performance async ASGI server with automated Swagger docs (`/docs`).
- **Prompt Formulation**: Strictly enforces the fine-tuned sequence-to-sequence prompt format:
  `translate {region} to Bangla: {dialect_sentence}`
- **Generation Settings**: Uses exact validated decoding parameters:
  - `num_beams = 4`
  - `max_new_tokens = 32`
  - `length_penalty = 1.0`
- **Hugging Face Serverless Inference**: Direct connection to Hugging Face Inference API with automatic 503 cold-start status handling.
- **In-Memory Checkpoint Predictions**: 1,419 verified test sentence translations loaded for instant local demonstration.
- **Docker Support**: Ready for deployment on Render, Railway, Hugging Face Spaces, or Docker Desktop.

---

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run API Server
```bash
python run.py
```
The API server will be live at: **http://127.0.0.1:8000**
Interactive API Documentation: **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

### 1. `POST /api/translate`
Translate a dialect sentence to Standard Bengali.

**Request Body:**
```json
{
  "region": "Chittagong",
  "sentence": "তোঁয়ার তু কি বই পরার অভ্যাস আছে নেকি",
  "hf_repo_id": "samim5669/banglat5-dialect-to-standard",
  "hf_api_token": "hf_xxxxxxxxxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "translation": "তোমার কি বই পড়ার অভ্যাস আছে?",
  "mode": "huggingface",
  "prompt_used": "translate Chittagong to Bangla: তোঁয়ার তু কি বই পরার অভ্যাস আছে নেকি"
}
```

### 2. `GET /api/health`
Health check and supported regions.

### 3. `GET /api/insights`
Returns full thesis experimental benchmarks (BLEU: 50.87, chrF: 75.34, BERTScore: 0.9392, STS: 0.9244).

### 4. `POST /api/settings/verify`
Verify Hugging Face model repository accessibility and token validity.

---

## 🐳 Docker Deployment

Build and run using Docker:
```bash
docker build -t bangla-dialect-api .
docker run -p 8000:8000 bangla-dialect-api
```

---

## 🧪 Automated Testing
Run the complete test suite:
```bash
pytest tests/ -v
```
