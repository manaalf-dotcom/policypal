# ==============================
# PolicyPal Configuration File
# ==============================

# ========= Step 3: Parsing & Chunking =========
INPUT_PDF_DIR        = "data/sample_policies"
OUTPUT_CHUNKS_PATH   = "storage/parsed_chunks.json"

TOKEN_CHUNK_SIZE     = 800
TOKEN_CHUNK_OVERLAP  = 100
TOKEN_ENCODING_NAME  = "cl100k_base"
MIN_CHUNK_CHARS      = 300

# ===== Step 4: Embeddings + Vector Store =====
CHROMA_PERSIST_DIR      = "storage/chroma"
CHROMA_COLLECTION_NAME  = "policypal_chunks"

EMBEDDING_MODEL  = "models/text-embedding-004"   # Gemini embedding model
RETRIEVAL_TOP_K  = 3

# ===== Step 5: RAG Answer Generation =====
CHAT_MODEL      = "gemini-1.5-flash"
MAX_CONTEXT_CHARS       = 12000
RAG_TOP_K               = 3
RAG_DISTANCE_THRESHOLD  = 1.2

# Step 6: Intent Classification
INTENT_MODEL         = "gemini-1.5-flash"
ENABLE_INTENT_ROUTER = True
