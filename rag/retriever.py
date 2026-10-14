"""
rag/retriever.py
Hybrid Regulatory Retriever with:
1. Stopword filtering & relevance thresholds.
2. TTL (Time-To-Live) In-Memory Query Cache with hit/miss tracking.
3. Cache purge controls.
"""

import re
import time
from rag.loader import load_regulatory_corpus
from rag.chunker import chunk_document

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
    "t", "can", "will", "just", "don", "should", "now", "something", "love", "dummy",
    "new", "rule", "rules", "circular", "circulars", "direction", "directions",
    "master", "act", "acts", "abotut", "regarding", "tell", "give", "show", "find",
    "latest", "recent", "today", "yesterday", "tomorrow", "update", "updates", "say", "says",
    "please", "help", "hey", "hi", "hello", "know", "knows", "known", "knew", "knowing",
    "ask", "asks", "asked", "check", "checks", "checked", "see", "look", "want", "need"
}

# Ubiquitous boilerplate words that appear in virtually every RBI document.
# Matching solely these words provides zero topical evidence.
UBIQUITOUS_CORPUS_TERMS = {
    "rbi", "bank", "banks", "banking", "reserve", "india", "clause", "section",
    "guideline", "guidelines", "order", "document", "documents", "paragraph"
}

# Restricted non-banking topics with zero underwriting relevance
RESTRICTED_TOPICS = {
    "pm", "prime", "minister", "politics", "president", "election", "modi",
    "cricket", "bollywood", "pizza", "rocket", "alien"
}

RELEVANCE_THRESHOLD = 5.0
DEFAULT_CACHE_TTL_SECONDS = 300 # 5 minutes

class RegulatoryRetriever:
    def __init__(self, corpus_dir: str = "data/rbi_regulatory_corpus", cache_ttl: int = DEFAULT_CACHE_TTL_SECONDS):
        self.corpus_dir = corpus_dir
        self.cache_ttl = cache_ttl
        self.chunks = []
        
        # TTL Query Cache: {normalized_query: {"timestamp": float, "results": list}}
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        self._initialize_index()
        
    def _initialize_index(self):
        docs = load_regulatory_corpus(self.corpus_dir)
        for doc in docs:
            self.chunks.extend(chunk_document(doc))

    def add_document(self, source_name: str, content: str) -> int:
        """Dynamically chunks and indexes a newly uploaded document, purging cache."""
        new_chunks = chunk_document({"source": source_name, "content": content})
        self.chunks.extend(new_chunks)
        self.purge_cache()
        return len(new_chunks)
            
    def purge_cache(self) -> int:
        """Purges all entries from the TTL query cache."""
        count = len(self.cache)
        self.cache.clear()
        return count
        
    def get_cache_stats(self) -> dict:
        """Returns real-time telemetry metrics for the cache."""
        total_requests = self.cache_hits + self.cache_misses
        hit_ratio = round((self.cache_hits / total_requests * 100), 1) if total_requests > 0 else 0.0
        return {
            "cached_entries": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio_pct": hit_ratio,
            "ttl_seconds": self.cache_ttl
        }
            
    def retrieve(self, query: str, top_k: int = 3) -> tuple[list[dict], bool]:
        """
        Retrieves top relevant chunks with TTL caching and strict abstention SLA.
        Returns: (results_list, was_cache_hit)
        """
        normalized_key = " ".join(re.findall(r'\b[a-z0-9]+\b', query.lower()))
        now = time.time()
        
        # 1. Check TTL Cache
        if normalized_key in self.cache:
            entry = self.cache[normalized_key]
            if now - entry["timestamp"] < self.cache_ttl:
                self.cache_hits += 1
                return entry["results"][:top_k], True
            else:
                # Expired TTL
                del self.cache[normalized_key]
                
        self.cache_misses += 1
        
        # 2. Tokenize (preserve 2+ character domain terms like 'pm', 'ltv', 'kyc')
        raw_tokens = re.findall(r'\b[a-z0-9]+\b', query.lower())
        
        # Immediate abstention on out-of-scope non-banking topics
        if any(t in RESTRICTED_TOPICS for t in raw_tokens):
            return [], False

        content_tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) >= 2]
        
        if not content_tokens:
            return [], False
            
        token_set = set(content_tokens)
        scored = []
        
        for c in self.chunks:
            text_lower = c["text"].lower()
            chunk_tokens = set(re.findall(r'\b[a-z0-9]+\b', text_lower))
            
            matched = token_set.intersection(chunk_tokens)
            coverage = len(matched) / len(token_set)
            
            # Rule A: Reject matches that consist SOLELY of ubiquitous corpus header terms
            substantive_matches = matched.difference(UBIQUITOUS_CORPUS_TERMS)
            if not substantive_matches:
                continue
                
            # Rule B: Require at least 2 distinct tokens for multi-word queries
            if len(token_set) > 1 and len(matched) < 2:
                continue
                
            # Rule C: Token coverage threshold >= 35%
            if coverage < 0.35:
                continue
                
            score = (len(matched) * 4.0) + (coverage * 5.0) + (len(substantive_matches) * 2.0)
            for token in matched:
                score += min(5, text_lower.count(token)) * 0.5
                
            if score >= RELEVANCE_THRESHOLD:
                scored.append({
                    "score": round(score, 2),
                    "source": c["source"],
                    "chunk_id": c["chunk_id"],
                    "matched_tokens": list(matched),
                    "text": c["text"]
                })
                
        scored.sort(key=lambda x: x["score"], reverse=True)
        results = scored[:top_k]
        
        # Cache results with timestamp
        self.cache[normalized_key] = {
            "timestamp": now,
            "results": results
        }
        
        return results, False

