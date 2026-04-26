BASE_DOCUMENTS = [
    """
    Distributed systems rely on coordination among independent nodes.
    Common challenges include partial failures, unreliable networks,
    concurrency, ordering, replication, and consistency. Systems often
    use caching, replication, leader election, leases, heartbeats, and
    consensus protocols to improve reliability and performance.
    """ * 80,

    """
    Large language model inference has two major phases: prefill and decode.
    During prefill, the model processes the input prompt and builds the
    key-value cache. During decode, the model generates output tokens
    incrementally. Reusing KV cache for repeated prefixes can reduce
    time to first token and save GPU computation.
    """ * 80,

    """
    Cache eviction policies decide what data to remove when memory is full.
    LRU evicts the least recently used item. LFU evicts the least frequently
    used item. Semantic-aware policies may preserve entries likely to be
    useful for related future requests. Learned policies use features to
    estimate future reuse probability.
    """ * 80,
]


QUESTIONS = [
    "Summarize the key idea in three bullet points.",
    "What are the main performance bottlenecks?",
    "Explain this in simple terms for a beginner.",
    "Give one example where this would be useful.",
    "What metrics should we use to evaluate this?",
]


def build_prompt(document: str, question: str) -> str:
    return f"""
You are given the following document.

DOCUMENT:
{document}

QUESTION:
{question}

ANSWER:
"""