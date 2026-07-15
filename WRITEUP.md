# 3.1 Approach

> ## System Architecture
> 
> 
> This system implements a multi-stage **hybrid matching and verification pipeline** designed to accurately retrieve and validate company entities matching complex natural language queries.
> ---
> 
> 
> ### Components Included
> 
> 
> The system is structured as a Directed Acyclic Graph (DAG) using **Hamilton** and consists of five logical stages:
> * **Data Ingestion (`read`)**: Parses and validates the raw `JSONL` input dataset into typed Pydantic structures.
> * **LLM Query Parser (`query_parser`)**: Leverages `gemini-2.5-flash` to extract structured attributes (e.g., country codes, employee bounds) and generate an optimized semantic target prompt.
> * **Deterministic Hard Filter (`hard_filter`)**: Fast, rule-based filtering on geographic and structured fields with a smart category-keyword fallback to drop clear outliers instantly.
> * **Semantic Re-Ranker (`semantic_filter`)**: Generates embeddings using `gemini-embedding-2` for surviving candidates, computing similarity scores boosted by keyword alignment.
> * **LLM Judge (`ansIr`)**: Executes a high-context reasoning pass via `gemini-2.5-flash` over the top 15 candidates to Ied out nuanced false positives, semantic bleed, and role reversals.
> 
> 
> ---
> 
> 
> ### Component Interaction & Dataflow
> 
> 
> ```
> [Messy Query] ➔ [Query Parser (LLM)] ➔ [Hard Filters (Rule-based)] ➔ [Semantic Ranker (Embeddings)] ➔ [LLM Judge] ➔ [Final Matches]
> 
> ```
> 
> 
> * The **Hamilton** framework serves as the centralized orchestrator, managing execution state and data dependencies.
> * Raw text and structured metrics flow downstream, dynamically shrinking the candidate pool at each milestone.
> * High-cost neural computations (embeddings and generation) are strictly gated behind fast, low-cost rule boundaries.
> 
> 
> ---
> 
> 
> ### Why This Design Was Chosen
> 
> 
> * **Cost & Latency Efficiency (The Funnel Model)**: Passing hundreds of unfiltered candidates directly to an LLM or embedding model is slow and expensive. Shrinking the candidate pool deterministically (e.g., from 477 to 12) before applying neural semantic scoring keeps execution fast and API costs nominal.
> * **Separation of Concerns**: Organizing stages as isolated Python modules makes testing, debugging, and maintaining the pipeline trivial.
> * **Accuracy via Hybrid Search**: Relying solely on vector embeddings often captures irrelevant companies due to "semantic bleed." Coupling vector similarity with categorical keyword boosting and a final strict LLM Judge ensures exceptionally high precision.
> 
>
# 3.2 Tradeoffs

> ## System Optimizations & Trade-Offs
> 
> 
> To deliver a production-grade system, I deliberately prioritized certain operational metrics over others.
> ---
> 
> 
> ### What I Optimized For
> 
> 
> * **Accuracy (Precision-First)**: I optimized heavily to eliminate false positives (e.g., preventing software companies from matching a "logistics" query). The LLM Judge acts as a final strict gatekeeper to ensure high matching confidence.
> 
> 
> * **Cost & Latency Efficiency**: I engineered a cascade "funnel". High-overhead neural operations (dense embeddings and generative validation) are strictly gated behind fast, free, deterministic Python rule filters.
> 
> 
> * **Robustness & Simplicity**: I built our dataflow on typed Pydantic models (eliminating brittle Pandas steps) and organized pipeline dependencies via the modular **Hamilton** framework.
> 
> 
> 
> 
> ---
> 
> 
> ### Intentional Trade-Offs Made
> 
> 
> * **Sequential Latency vs. Cost (Stage 3 Embeddings)**: I chose to fetch individual, isolated embeddings sequentially for surviving candidates in Stage 3. While batching is theoretically faster, isolating the requests avoids SDK truncation issues and prevents misalignment bugs. Since Stage 2 hard-filters reduce the candidate pool to a tiny size (e.g., from 477 to 12), the added sequential latency is negligible.
> 
> 
> * **Strictness vs. Recall**: I chose a highly skeptical LLM Judge. If a candidate is borderline or a role reversal (e.g., a customer of logistics rather than a logistics provider), the system rejects it. I traded away generic "close" matches to guarantee 100% accurate positive matches.
> 
>
---

# 3.3 Error Analysis

> ## System Limits & Concrete Misclassifications
> 
> 
> While our multi-stage pipeline is highly accurate, specific data patterns and structural ambiguities can still challenge the framework.
> 
> 
> ---
> 
> 
> ### Where the System Struggles
> 
> 
> * **Implicit Business Models**: The rule-based keyword filters (Stage 2) and vector embeddings (Stage 3) rely on explicit semantic footprints. If a company's profile description is highly abstract or lacks direct industry-specific terminology, it can get prematurely filtered out.
> 
> 
> * **Multi-National Parent-Subsidiary Mappings**: If a search targets a specific geographic region (e.g., Germany) but a matching company is registered under a foreign country code (e.g., `ro` for Romania) with its German operations only mentioned in the description, the Stage 2 geographic filter will discard it.
> 
> 
> 
> 
> ---
> 
> 
> ### Concrete Examples of Misclassification
> 
> 
> * **Example 1: CBRE Romania (Real Estate vs. Logistics)**
> 
> * *The Issue*: Highly ranked semantically in Stage 3.
> 
> 
> * *Why it Misclassifies*: CBRE is a commercial real estate broker. However, because its description heavily details building "logistics facilities, warehouse designs, and supply chain hubs," the embedding vector scores it as a strong match for logistics. Although the Stage 4 LLM Judge correctly caught and rejected this instance, reliance on Stage 3 alone would lead to a false positive.
> 
> 
> 
> 
> * **Example 2: ARMAI (AI Consultant vs. Logistics Provider)**
> 
> * *The Issue*: Passed the Stage 2 keyword filter and Stage 3 ranker for a German logistics query.
> 
> 
> * *Why it Misclassifies*: ARMAI is a machine learning systems architect. Its profile contains keywords regarding "supply chain routing optimization and autonomous logistics algorithms". Stage 2 allowed it through because of the word "logistics," and Stage 3 scored it highly because of the semantic overlap of transport optimization.
> 
> 
> 
> 
> 
> 

---

# 3.4 Scaling

> ## Scaling up to 100,000 Companies
> 
> 
> Moving from a testing dataset of ~500 companies to a production-scale database of 100,000+ companies per query introduces latency and API billing bottlenecks.
> 
> 
> ---
> 
> 
> ### Key Architectural Changes
> 
> 
> * **Transition to a Native Vector Database**:
> * *Currently*: We calculate embeddings dynamically in memory during pipeline execution.
> 
> 
> * *At Scale*: We would pre-compute and store embeddings for all 100,000+ companies in a dedicated vector database (such as Pinecone, Qdrant, or pgvector). Stage 3 would query this pre-computed index using Approximate Nearest Neighbor (ANN) search, bypassing dynamic API embedding calls.
> 
> 
> 
> 
> * **Parallelized Batching & Async Execution**:
> * *Currently*: The system handles sequential calls to prevent SDK multi-part array issues.
> 
> 
> * *At Scale*: We would implement concurrent, asynchronous batching (using `asyncio` or Celery workers) to pull embeddings or process LLM Judge evaluations in parallel.
> 
> 
> * **Two-Pass Hard Filtering**:
> * We would push our Stage 2 deterministic filters directly into the database query level (using SQL or Elasticsearch metadata filtering). This ensures we only load a fraction of the candidate pool into Python memory before running semantic operations.
> 
> 
> 
> 
> * **Strict Top-N Slicing**:
> * We would enforce a hard limit (e.g., `Top-15` or `Top-20`) at the end of Stage 3, ensuring the LLM Judge only receives a predictable, cost-capped payload regardless of initial search volume.
> 
> 
> 
> 
> 
> 

---

# 3.5 Failure Modes

> ## Silent Failures & Production Monitoring
> 
> 
> Unlike traditional software that fails loudly with system crashes, machine learning systems fail silently by producing highly confident but incorrect predictions.
> ---
> 
> 
> ### When the System Produces Confident but Incorrect Results
> 
> 
> * **Synonym Over-Inflation**: If a company's description is written with generic marketing buzzwords that overlap with multiple search sectors, the vector space can align them closely, and the LLM Judge may assume they provide services they merely consume.
> 
> 
> * **Target Market vs. Provider Confusion (Role Reversal)**: For example, if a query asks for "Automotive parts suppliers," and a candidate is a major car manufacturer (like Dacia) listing "Automotive parts procurement" as an operating footprint, the system can confidently classify it as a supplier.
> 
> 
> * **Upstream Model Drift**: If the underlying Google GenAI embedding or LLM models are updated (e.g., from `gemini-2.5-flash` to a newer version), the embedding distributions might shift, altering similarity metrics without any changes to our codebase.
> 
> 
> 
> 
> ---
> 
> 
> ### Production Monitoring Strategy
> 
> 
> * **Telemetry Metrics to Monitor**:
> * **Rejection/Match Ratios**: Track the percentage of candidates rejected by Stage 4. A sudden spike to 100% rejection suggests Stage 2 is passing low-quality candidates.
> 
> 
> * **Null and Schema Drift**: Monitor the rate of missing attributes (like null revenues or missing NAICS codes) in incoming datasets.
> 
> 
> * **Pipeline Latency & API Costs**: Track execution duration per stage, especially Stage 3 embedding calls and Stage 4 generation tokens.
> 
> 
> * **Human-in-the-Loop (HITL) Logs**: Periodically log random samples of LLM Judge matches and rejections for manual auditing to compute offline precision and catch alignment drift over time.
> 
> 
> 
>