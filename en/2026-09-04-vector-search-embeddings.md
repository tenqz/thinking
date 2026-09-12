---
date: 2026-09-04
author: Oleg Patsay
slug: vector-search-embeddings
excerpt: "Traditional search compares lexical signals. Vector search compares embeddings, allowing semantically similar objects to appear close together even when their wording barely overlaps."
---

# Vector Search and Embeddings: How Semantic Search Works

Search has an obvious problem that we spent years solving with different workarounds. Suppose a database contains a document called “Cancellation and Refund Policy,” while the user searches for “how do I get my money back for a purchase?” A human immediately sees that the two are related. A conventional lexical search has a harder time: “get my money back” and “refund policy” are semantically close to us, but their literal word overlap is weak.

Vector search approaches the problem differently.

Instead of comparing only words, it represents objects as vectors — arrays of numbers produced by an embedding model.

For example:

```text
"how do I get my money back for a purchase"
↓
[0.018, -0.342, 0.721, 0.114, ...]
```

A document gets its own vector. A query gets another. Then the search system finds vectors that are close to the query vector.

The important part is not that the database somehow “understands meaning.” It does not.

The embedding model has learned a representation space in which certain kinds of similarity are reflected by distance.

That difference matters when trying to understand what semantic search actually does.

## How text becomes a vector

An embedding model takes an object — commonly text — and returns an array of floating-point numbers.

For example:

```text
[0.018, -0.342, 0.721, 0.114, ...]
```

Real embedding vectors often have hundreds or thousands of dimensions.

It is tempting to imagine that each dimension corresponds to some human concept: one coordinate for “finance,” another for “positive sentiment,” another for “PHP.” Dense embeddings usually do not work that way. Meaning is distributed across many dimensions, and individual coordinates are not normally interpretable on their own.

What matters is the geometry of the representation.

Imagine three sentences:

```text
A: How can I get a refund for my subscription?
B: I want to cancel my paid plan and get my money back.
C: How do I cook carbonara?
```

An embedding model trained for semantic representation should usually place A and B closer together than either of them is to C.

That is the core idea.

A useful caution is to avoid saying that an embedding “stores the meaning of the text” as if it were a perfect semantic encoding. It stores a learned numerical representation. What counts as similar depends on the model, its training, and the domain in which you use it.

## Vector space and distance between objects

To make the idea visible, imagine a two-dimensional space:

```text
A = [1.2, 3.1]
B = [1.4, 3.0]
C = [8.7, 1.1]
```

A and B are close.

C is much farther away.

Real embeddings live in far more dimensions, but the principle is the same.

The search system needs a metric for deciding what “close” means.

Common choices include:

- cosine similarity;
- dot product;
- Euclidean distance.

Cosine similarity is often written as:

```text
cosine_similarity(A, B) =
(A · B) / (||A|| × ||B||)
```

Intuitively, it compares the angle between vectors rather than only their absolute magnitude.

But there is no universal rule that cosine is always the right metric. The embedding model or its documentation usually specifies which similarity function is appropriate. It is better to follow the model's assumptions than to choose cosine simply because it appears in many tutorials.

## How vector search works

Now we can assemble the process.

Suppose we have ten thousand documents. First, each document is passed through the embedding model:

```text
Document 1
↓
Embedding model
↓
Vector 1

Document 2
↓
Embedding model
↓
Vector 2

...

Document 10000
↓
Embedding model
↓
Vector 10000
```

The vectors are stored alongside identifiers for the source documents.

Usually we also store metadata: category, date, user, language, access rights, or any other fields that may later be useful for filtering.

Then the user enters a query:

> How do I get a refund for my subscription?

The query goes through the same embedding model:

```text
Query
↓
Embedding model
↓
Query vector
```

Now we have one new vector and thousands of document vectors.

The remaining task is to find the nearest ones:

```text
Query vector
     ↓
similarity search
     ↓
Vector 182
Vector 914
Vector 72
     ↓
source documents
```

That is vector search at the conceptual level.

The model handles representation.

The search system finds nearby representations.

The database does not need to understand what “refund” means. It only needs to efficiently compare numerical objects produced by the model.

## Why not compare the query with every vector?

For a small collection, you can.

Exact nearest-neighbor search can calculate the distance from the query to every stored vector, sort the results, and return the nearest ones.

That is conceptually simple and exact.

The problem appears when the dataset grows to hundreds of thousands, millions, or billions of vectors.

Comparing a high-dimensional query vector with every stored vector becomes expensive.

This is similar to an ordinary database query without an index.

You can search like this:

```sql
SELECT *
FROM users
WHERE email = 'user@example.com';
```

If there is no useful index, the database may have to inspect far more rows than necessary.

Vector search has the same general need: some structure that reduces the amount of work required to find promising neighbors.

That leads to the distinction between exact and approximate search:

```text
Exact search
slower at scale
exact nearest neighbors

Approximate search
faster at scale
may miss some ideal neighbors
```

Approximate Nearest Neighbor algorithms trade a small amount of recall for a large performance improvement.

For a small dataset, exact search may be perfectly reasonable. “Vector search” does not automatically mean that a sophisticated ANN index is required.

## What is ANN and where does HNSW fit?

ANN stands for Approximate Nearest Neighbor search.

It is a family of approaches rather than one specific algorithm.

One of the most widely used vector indexes is HNSW — Hierarchical Navigable Small World.

The intuition can be described as a graph.

Instead of checking every vector, the algorithm creates links between points and uses those links to move quickly toward promising areas of the space.

The “hierarchical” part adds several graph layers. Upper layers contain a sparser navigation structure that helps make large jumps; lower layers contain denser neighborhoods for more precise search.

A city analogy is useful.

If you need an address on the other side of a country, you do not inspect every street in every city. You first choose the region, then the city, then the neighborhood, and only then the local street.

HNSW uses a roughly similar idea in vector space: reach a promising region quickly and refine from there.

The trade-offs are tunable. Index construction cost, memory usage, query speed, and recall can be adjusted through parameters.

The important point is that HNSW does not understand semantics.

It knows how to navigate a graph of vectors efficiently.

Semantics entered earlier, when the embedding model created the vectors.

## What does a vector database actually do?

After learning about embeddings, it is easy to imagine a vector database as a fundamentally new kind of storage that somehow understands AI.

Its job is more familiar than that.

It needs to store something like:

```text
id

vector

payload / metadata
```

and efficiently answer a request such as:

> Find the ten vectors nearest to this query vector, but only among documents belonging to user 42 and only from the last year.

As soon as you add that condition, ordinary database concerns return:

- filtering;
- updates;
- deletion;
- persistence;
- replication;
- distributed storage;
- access controls;
- indexing.

The vector index accelerates neighbor search.

The payload tells you what each vector represents.

Filters prevent you from searching the entire space when only one subset of the data is relevant.

Dedicated products such as Qdrant, Pinecone, and Weaviate focus heavily on these workloads. But vector support also exists in more general systems including PostgreSQL, Elasticsearch, MongoDB, and others.

That means “we need semantic search” does not automatically imply “we need a separate vector database.”

The right choice depends on data volume, filtering needs, operational constraints, latency targets, and the infrastructure you already have.

## Vector search and lexical search solve different problems

Semantic search is powerful, but conventional lexical search did not suddenly become obsolete.

There are queries where exact text is exactly what you want.

For example:

```text
ERR_CONNECTION_RESET
SKU-89431
PHP 8.2.17
InvoiceAccessPolicy
```

A lexical index is excellent at matching identifiers, error messages, product codes, versions, names, and exact terms.

Vector search shines when the wording differs but the intended concept is similar.

A user searches:

> how do I get my money back?

while the document is called:

```text
Cancellation and Refund Policy
```

Or the query says:

> vacation rules

while the documentation says:

```text
Annual Leave Policy
```

A simplified distinction is:

```text
Keyword / lexical search
→ what is written
```

versus:

```text
Vector search
→ what is similar in the learned representation
```

Of course, modern lexical ranking such as BM25 is more sophisticated than literal string equality. But the main signal still comes from lexical features, while vector search uses a learned representation.

## Why hybrid search is becoming common

Because the two approaches have different strengths, production search increasingly combines them.

A basic hybrid pipeline looks like this:

```text
              ┌→ lexical search ─┐
Query ────────┤                  ├→ merge → ranking
              └→ vector search ─┘
```

Suppose the query is:

```text
OAuth refresh token rotation
```

Lexical search is valuable because `OAuth`, `refresh token`, and specific identifiers are exact technical terms.

Vector search is useful because a relevant document may use nearby phrasing such as “renewal credentials” or describe the same concept without matching every token.

The two result sets can be merged with a fusion strategy such as Reciprocal Rank Fusion, then optionally reranked with a stronger model or business-specific ranking rules.

For production systems, this often looks much healthier than the slogan “we now search only by meaning.”

Exact terms did not disappear.

People still search for order numbers, class names, errors, SKUs, versions, and names.

Semantic retrieval simply adds another strong signal.

Google illustrates the same idea in product search: full-text retrieval can precisely match a concrete model number, while vector search can find products similar by description. The two signals serve different query types.

## What does this have to do with RAG?

Vector search is now frequently discussed together with RAG, even though vector retrieval did not originate with LLMs.

A simple RAG indexing pipeline looks like this:

```text
Documents
↓
chunks
↓
embeddings
↓
vector database
```

When a user asks a question:

```text
Question
↓
embedding
↓
vector search
↓
relevant chunks
↓
LLM context
↓
answer
```

Vector search acts as the retrieval layer. It tries to find document fragments whose representations are close to the question, then passes those fragments into the LLM context.

This exposes an important limitation: RAG quality depends on more than the language model.

If retrieval finds the wrong documents, the LLM receives the wrong context. You can improve the prompt indefinitely, but the answer is still built from what the system managed to retrieve.

A good RAG system therefore requires decisions about:

- chunking;
- embedding model choice;
- metadata filters;
- hybrid retrieval;
- reranking;
- `top_k`;
- document freshness;
- access control.

Vector search is one component of retrieval, not a complete RAG architecture.

This connects directly to Context Engineering: retrieval is valuable because it lets the model see a relevant part of a much larger knowledge base at the right time.

## Embeddings are used for much more than text

Text is the most visible example, but an embedding is a general representation technique.

Images can be embedded so that visually or semantically similar images end up near each other.

Audio can be embedded.

Users and products can be represented as vectors for recommendation systems.

Embeddings can also support:

- clustering;
- classification;
- anomaly detection;
- deduplication;
- recommendation;
- reverse image search;
- multimodal retrieval.

In a multimodal model, a text query such as:

> a red car on a snowy road

can be represented in a space compatible with image embeddings, allowing the system to retrieve images matching the description.

The general pattern stays the same: turn objects into numerical representations and use geometry to compare them.

## What vector search cannot do

It is easy to overestimate semantic search after the first impressive demo.

There are several limitations worth keeping explicit.

First, the embedding model may not represent your domain well. A general-purpose model may miss distinctions that matter in legal, medical, scientific, financial, or highly specialized technical text.

Second, similarity is not the same as business relevance. Two documents can be thematically similar while only one is valid for the current customer, region, product version, or date.

Third, approximate search can miss ideal neighbors by design.

Fourth, chunk size changes retrieval behavior. A tiny fragment may lose meaning; a huge fragment may produce a vague representation.

Fifth, freshness matters. If the source document changes, its embedding may need to be regenerated.

Sixth, embeddings from different models generally should not be mixed blindly in one index. The numerical coordinates belong to the representation space of the model that produced them.

And one subtle point: a similarity score such as `0.83` does not mean “83% correct.”

The score is a value produced by a similarity function in a particular embedding space.

There is no universal threshold such as “everything above 0.8 is relevant.”

Thresholds need to be calibrated on the actual model, data, and task.

Vector similarity is a strong signal.

It is not a truth probability.

## How I now think about semantic search

I find it useful to separate semantic search into three different engineering problems.

First, **representation**.

Which embedding model turns objects into vectors, and what kinds of similarity does that representation preserve?

Second, **retrieval**.

How do we efficiently find nearby vectors — exact KNN, ANN, HNSW, or another index?

Third, **ranking**.

How do we combine vector similarity with metadata filters, lexical search, reranking, freshness, and business rules?

The pipeline looks like this:

```text
Representation
Embedding model
      ↓
Vector space
      ↓
Retrieval
KNN / ANN
      ↓
Ranking
Hybrid / reranking / rules
      ↓
Result
```

A vector database does not understand text.

HNSW does not know what a refund is.

Cosine similarity does not know user intent.

The embedding model builds a numerical space in which useful relationships may be reflected by geometry. The search infrastructure finds neighbors in that space. Ranking decides which of those neighbors are actually useful for the product.

That is the part hidden behind the convenient phrase “search by meaning.”

## What to read next

- [Context Engineering: What It Is and How to Manage LLM Context](/context-engineering)
- [What Is MCP (Model Context Protocol) and How Does It Work?](/model-context-protocol-mcp)

---

## Let's make the complex understandable.

Architecture, engineering leadership, and AI in development — when the system is too important to simplify, and too expensive not to own.

**Oleg Patsay**

- Telegram: [t.me/opatsay](https://t.me/opatsay)
- Website: [opatsay.com](https://opatsay.com/)
- [LinkedIn](https://www.linkedin.com/in/oleg-patsay)
- [Email](mailto:opatsay@gmail.com)
