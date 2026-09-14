from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.config import (
    VALID_REGIONS,
    DEFAULT_HF_REPO_ID,
    DEFAULT_HF_API_TOKEN,
    MAX_SOURCE_LEN,
    MAX_TARGET_LEN,
    NUM_BEAMS,
)
from backend.hf_client import query_translation, verify_hf_credentials

app = FastAPI(
    title="Bangla Regional Dialect Translator API",
    description="Backend API powering the BanglaT5 regional dialect translation interface.",
    version="1.0.0",
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------
class TranslateRequest(BaseModel):
    region: str = Field(..., description="One of the 7 valid Bangladeshi dialect regions")
    sentence: str = Field(..., description="Dialect sentence in Bengali script")
    hf_repo_id: Optional[str] = Field(None, description="Optional custom Hugging Face Model Repo ID")
    hf_api_token: Optional[str] = Field(None, description="Optional custom Hugging Face API Token")

class VerifySettingsRequest(BaseModel):
    hf_repo_id: str = Field(..., description="Hugging Face repo name e.g. username/banglat5-dialect")
    hf_api_token: Optional[str] = Field("", description="Hugging Face User Access Token")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.get("/")
@app.head("/")
async def root():
    """Welcome endpoint providing service status and quick links."""
    return {
        "status": "online",
        "name": "Bangla Regional Dialect Translator API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/api/health",
        "translate_endpoint": "/api/translate",
        "insights_endpoint": "/api/insights",
    }


@app.get("/favicon.ico")
async def favicon():
    from fastapi import Response, status
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.get("/api/health")
async def health_check():
    """Returns system status, active configuration and supported regions."""
    return {
        "status": "healthy",
        "default_repo_id": DEFAULT_HF_REPO_ID,
        "token_configured": bool(DEFAULT_HF_API_TOKEN),
        "valid_regions": VALID_REGIONS,
        "parameters": {
            "max_source_len": MAX_SOURCE_LEN,
            "max_target_len": MAX_TARGET_LEN,
            "num_beams": NUM_BEAMS,
        }
    }


@app.get("/api/regions")
async def get_regions():
    """
    Returns authentic regional metadata, sample sentences and evaluation metrics
    directly from the research dataset and model evaluation.
    """
    from backend.hf_client import REAL_TEST_PREDICTIONS

    region_metadata = [
        {"id": "Chittagong", "nameEn": "Chittagong", "nameBn": "চট্টগ্রাম", "division": "দক্ষিণ-পূর্ব", "bleu": 31.63, "test_n": 113, "dataset_pairs": 1129},
        {"id": "Noakhali", "nameEn": "Noakhali", "nameBn": "নোয়াখালী", "division": "দক্ষিণ-পূর্ব", "bleu": 47.49, "test_n": 250, "dataset_pairs": 2492},
        {"id": "Barishal", "nameEn": "Barishal", "nameBn": "বরিশাল", "division": "দক্ষিণ", "bleu": 44.17, "test_n": 153, "dataset_pairs": 1499},
        {"id": "Rangpur", "nameEn": "Rangpur", "nameBn": "রংপুর", "division": "উত্তর", "bleu": 54.14, "test_n": 250, "dataset_pairs": 2496},
        {"id": "Pabna", "nameEn": "Pabna", "nameBn": "পাবনা", "division": "পশ্চিম", "bleu": 50.63, "test_n": 250, "dataset_pairs": 2498},
        {"id": "Mymensingh", "nameEn": "Mymensingh", "nameBn": "ময়মনসিংহ", "division": "উত্তর-মধ্য", "bleu": 41.73, "test_n": 153, "dataset_pairs": 1499},
        {"id": "Jashore", "nameEn": "Jashore", "nameBn": "যশোর", "division": "দক্ষিণ-পশ্চিম", "bleu": 69.31, "test_n": 250, "dataset_pairs": 2498},
    ]

    result = []
    for reg in region_metadata:
        rid = reg["id"]
        pairs = REAL_TEST_PREDICTIONS.get(rid, {})
        examples = []
        for dialect_text, std_text in pairs.items():
            if len(dialect_text) > 8 and dialect_text != std_text:
                examples.append(dialect_text)
                if len(examples) >= 4:
                    break

        result.append({**reg, "examples": examples})

    return result


@app.post("/api/translate")
async def translate_dialect(req: TranslateRequest):
    """
    Translates a dialect sentence into Standard Bengali using exact fine-tuned formatting.
    """
    clean_region = req.region.strip() if req.region else ""
    clean_sentence = req.sentence.strip() if req.sentence else ""

    if not clean_region:
        raise HTTPException(status_code=400, detail="Please select a region.")

    if clean_region not in VALID_REGIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region '{clean_region}'. Must be one of: {', '.join(VALID_REGIONS)}."
        )

    if not clean_sentence:
        raise HTTPException(
            status_code=400,
            detail="Please type a dialect sentence before clicking Translate."
        )

    result = await query_translation(
        region=clean_region,
        sentence=clean_sentence,
        custom_repo_id=req.hf_repo_id,
        custom_token=req.hf_api_token,
    )
    return result


@app.post("/api/settings/verify")
async def verify_settings(req: VerifySettingsRequest):
    """Verifies whether the provided Hugging Face model repository and token are accessible."""
    return await verify_hf_credentials(req.hf_repo_id, req.hf_api_token or "")


@app.get("/api/insights")
async def get_research_insights():
    """
    Returns verified experimental benchmarks and insights from the master thesis research file.
    """
    return {
        "title": "Preserving Dialects, Enhancing Communication: A Model For Translating Regional Bangladeshi Languages into Standard Bengali",
        "base_model": "csebuetnlp/banglat5",
        "total_parallel_pairs": 14130,
        "test_pairs": 1419,
        "overall_benchmarks": [
            {"model": "BanglaT5 (Final)", "bleu": 50.87, "chrf": 75.34, "bert_f1": 0.9392, "sts_cosine": 0.9195, "status": "Winner"},
            {"model": "mT5-base", "bleu": 47.60, "chrf": 72.75, "bert_f1": 0.9324, "sts_cosine": 0.9100, "status": "Comparison"},
            {"model": "mT5-small", "bleu": 43.58, "chrf": 70.06, "bert_f1": 0.9241, "sts_cosine": 0.8884, "status": "Comparison"},
        ],
        "per_region_banglat5": [
            {"region": "Jashore", "test_n": 250, "bleu": 69.31, "chrf": 86.98, "bert_f1": 0.9696, "sts_cosine": 0.9627, "exact_match": 41.20, "identical_in_data": 34.84},
            {"region": "Rangpur", "test_n": 250, "bleu": 54.14, "chrf": 79.40, "bert_f1": 0.9475, "sts_cosine": 0.9326, "exact_match": 26.40, "identical_in_data": 2.24},
            {"region": "Pabna", "test_n": 250, "bleu": 50.63, "chrf": 74.52, "bert_f1": 0.9349, "sts_cosine": 0.9076, "exact_match": 24.40, "identical_in_data": 0.92},
            {"region": "Noakhali", "test_n": 250, "bleu": 47.49, "chrf": 73.60, "bert_f1": 0.9357, "sts_cosine": 0.9260, "exact_match": 20.80, "identical_in_data": 0.64},
            {"region": "Barishal", "test_n": 153, "bleu": 44.17, "chrf": 71.36, "bert_f1": 0.9314, "sts_cosine": 0.9246, "exact_match": 17.65, "identical_in_data": 1.00},
            {"region": "Mymensingh", "test_n": 153, "bleu": 41.73, "chrf": 69.15, "bert_f1": 0.9273, "sts_cosine": 0.9146, "exact_match": 18.30, "identical_in_data": 1.07},
            {"region": "Chittagong", "test_n": 113, "bleu": 31.63, "chrf": 60.65, "bert_f1": 0.8976, "sts_cosine": 0.8685, "exact_match": 13.27, "identical_in_data": 0.44},
        ],
        "key_findings": [
            {
                "headline": "Dialect Linguistic Distance Correlates with Translation Complexity",
                "detail": "Chittagong has lowest lexical overlap (Jaccard similarity 0.07-0.14) and proved the most challenging dialect across all evaluated models (31.63 BLEU)."
            },
            {
                "headline": "Jashore Performance is Driven by High Lexical Overlap",
                "detail": "34.84% of Jashore's dataset pairs are naturally identical to Standard Bengali, which substantially explains its high BLEU score (69.31)."
            },
            {
                "headline": "Monolingual Pretraining Beats Multilingual Pretraining",
                "detail": "BanglaT5 outperformed both mT5-base (+3.27 BLEU) and mT5-small (+7.29 BLEU) across every single region."
            },
            {
                "headline": "Methodological Rigor: ID-Grouped Split Prevented Target Leakage",
                "detail": "A two-stage split with ID-grouping and target deduplication eliminated multi-regional answer memorization, producing genuinely reproducible results."
            }
        ]
    }
