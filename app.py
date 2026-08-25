import os
import sys
import time
import streamlit as st

# Ensure project root and scripts directory are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
for path in [PROJECT_ROOT, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Page configuration
st.set_page_config(
    page_title="Energy Intelligence — AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme custom CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 20px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-title {
        color: #38bdf8;
        font-size: 2.0rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-bottom: 0px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-document { background-color: #065f46; color: #34d399; }
    .badge-weather { background-color: #1e40af; color: #60a5fa; }
    .badge-household { background-color: #5b21b6; color: #c084fc; }
    .badge-consumption { background-color: #9a3412; color: #fb923c; }
    .badge-hybrid { background-color: #854d0e; color: #facc15; }
    .badge-unknown { background-color: #374151; color: #9ca3af; }
    
    .answer-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 20px 24px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 16px;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #f8fafc;
    }
    .grounded-badge {
        background-color: #064e3b;
        border: 1px solid #059669;
        color: #a7f3d0;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .limited-badge {
        background-color: #854d0e;
        border: 1px solid #eab308;
        color: #fef08a;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .refusal-badge {
        background-color: #7f1d1d;
        border: 1px solid #dc2626;
        color: #fecaca;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .source-box {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 0.92rem;
        color: #cbd5e1;
        margin-bottom: 16px;
    }
    .chunk-box {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 6px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Lazy resource loader
@st.cache_resource
def get_pipeline():
    try:
        from scripts.pipeline import answer
        return answer
    except Exception as e:
        st.error(f"Failed to load backend pipeline: {e}")
        return None

# Sidebar: System Details
with st.sidebar:
    st.title("⚡ ENERGY INTELLIGENCE")
    st.caption("Grounded AI Assistant")
    st.markdown("---")
    
    st.subheader("⚙️ System Details")
    st.markdown("""
    - **Embedding**: `all-MiniLM-L6-v2 (384d)`
    - **Vector DB**: `ChromaDB` (`energy_documents`)
    - **Indexed Chunks**: `100`
    - **Primary LLM**: `Groq — openai/gpt-oss-120b`
    - **Fallback**: `OpenRouter`
    - **Data Scale**: `3.51M+ daily records`
    - **Households**: `5,566`
    - **Weather**: `882 records`
    - **Location**: `London, United Kingdom`
    """)

    st.markdown("---")
    st.caption("Hackathon Demo Ready v1.0 | Grounded Response Verified")

# Header Section
st.markdown("""
<div class="header-card">
    <div class="main-title">ENERGY INTELLIGENCE</div>
    <div class="sub-title">Ask a question about energy, weather, households, consumption, tariffs, or the provided documents.</div>
</div>
""", unsafe_allow_html=True)

# Quick Demo Query Buttons
st.markdown("##### 💡 Example Questions")
c1, c2, c3, c4, c5, c6 = st.columns(6)

example_selected = None
if c1.button("🌤️ Temp & Energy", use_container_width=True):
    example_selected = "How does temperature affect energy consumption?"
elif c2.button("📊 Avg Usage", use_container_width=True):
    example_selected = "What is the average energy consumption?"
elif c3.button("🏠 Household Stats", use_container_width=True):
    example_selected = "What household characteristics are available?"
elif c4.button("🪑 Chair Paper", use_container_width=True):
    example_selected = "How does the energy conserving chair work?"
elif c5.button("🔗 Weather & Usage", use_container_width=True):
    example_selected = "How does weather affect household energy consumption?"
elif c6.button("🧪 Refusal Test", use_container_width=True):
    example_selected = "What is the capital of France?"

# Query Input Box & Ask Button
st.markdown("---")
q_col, btn_col = st.columns([5, 1])

with q_col:
    query_val = st.text_area(
        "Type your question here...",
        value=example_selected if example_selected else "",
        placeholder="e.g. How does temperature affect energy consumption?",
        label_visibility="collapsed",
        height=100
    )

with btn_col:
    ask_btn = st.button("ASK ➔", type="primary", use_container_width=True)

# Auto-trigger if example clicked or ASK button pressed
if (ask_btn or example_selected) and query_val:
    with st.spinner("Processing query..."):
        pipeline_fn = get_pipeline()
        
        if pipeline_fn is None:
            st.error("Pipeline function unavailable.")
        else:
            try:
                res = pipeline_fn(query_val)
                
                if isinstance(res, dict):
                    answer_text = res.get("answer", "No answer generated.")
                    category = str(res.get("category", "UNKNOWN")).upper()
                    provider = res.get("provider", "Groq")
                    model_name = res.get("model", "openai/gpt-oss-120b")
                    latencies = res.get("latencies_ms", {})
                    sources = res.get("sources", {})
                    
                    router_lat = latencies.get("router", 0.0)
                    doc_lat = latencies.get("document_retrieval", 0.0)
                    tab_lat = latencies.get("tabular_retrieval", 0.0)
                    retrieval_lat = round(doc_lat + tab_lat, 2) if (doc_lat > 0 and tab_lat > 0) else max(doc_lat, tab_lat)
                    llm_lat = latencies.get("llm_generation", 0.0)
                    total_lat = latencies.get("end_to_end", 0.0)

                    tab_src = sources.get("tabular_source", "N/A")
                    retrieved_chunks = sources.get("retrieved_chunks", [])
                    
                    # Determine grounding status badge cleanly
                    ans_lower = answer_text.strip().lower()
                    is_pure_refusal = (
                        ans_lower.startswith("i don't have enough information") 
                        or ans_lower.startswith("i cannot answer")
                    ) and (len(answer_text.strip()) < 100 or (not retrieved_chunks and tab_src == "N/A"))
                    
                    if is_pure_refusal:
                        status_badge_html = '<span class="refusal-badge">🔴 SAFE REFUSAL</span>'
                    elif "however" in ans_lower or "limited" in ans_lower or "don't have enough information" in ans_lower:
                        status_badge_html = '<span class="limited-badge">🟡 LIMITED EVIDENCE</span>'
                    else:
                        status_badge_html = '<span class="grounded-badge">🟢 GROUNDED ANSWER</span>'

                    st.markdown("---")
                    
                    # 1. FINAL ANSWER — MAIN FOCUS
                    st.markdown(f"### 🤖 ANSWER &nbsp;&nbsp; {status_badge_html}", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="answer-card">
                        {answer_text}
                    </div>
                    """, unsafe_allow_html=True)

                    # 2. CONTEXT-AWARE METRICS PANEL
                    st.markdown("### 📊 QUERY & RETRIEVAL METRICS")
                    badge_class = f"badge-{category.lower()}" if category.lower() in ["document", "weather", "household", "consumption", "hybrid"] else "badge-unknown"
                    
                    st.markdown(f"**Query Route**: <span class=\"badge {badge_class}\">{category}</span>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Conditional metrics columns adapting to query type
                    if category.lower() in ["document", "hybrid"] and retrieved_chunks:
                        sim_scores = [c.get("similarity_score", 0.0) for c in retrieved_chunks]
                        top_sim = max(sim_scores) if sim_scores else 0.0
                        avg_sim = sum(sim_scores) / len(sim_scores) if sim_scores else 0.0
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Top-K Chunks", "5")
                        m2.metric("Top Cosine Sim", f"{top_sim:.4f}", help="Cosine similarity measures semantic relevance between the query and retrieved document chunks. Higher values indicate stronger semantic similarity. It is not answer accuracy.")
                        m3.metric("Avg Top-K Sim", f"{avg_sim:.4f}")
                        m4.metric("Doc Retrieval Latency", f"{doc_lat} ms")
                        
                        st.caption("Cosine similarity measures semantic relevance between the query and retrieved document chunks. Higher values indicate stronger semantic similarity. It is not answer accuracy.")

                    elif category.lower() in ["weather", "household", "consumption"] or tab_src != "N/A":
                        method = "DuckDB SQL" if "DuckDB" in tab_src else "Precomputed JSON"
                        t1, t2, t3 = st.columns(3)
                        t1.metric("Retrieval Method", method)
                        t2.metric("Tabular Retrieval Latency", f"{tab_lat} ms")
                        t3.metric("Data Source File", "analytical_dataset.csv")

                    st.markdown("---")

                    # 3. COMPACT SOURCE / LOCATION
                    st.markdown("### 📚 SOURCE")
                    src_items = []
                    
                    if retrieved_chunks:
                        top_chunk = sorted(retrieved_chunks, key=lambda x: (x.get("similarity_score") or 0.0), reverse=True)[0]
                        meta = top_chunk.get("metadata") or {}
                        fn = meta.get("file_name", "energy.pdf")
                        pg = meta.get("page", 1)
                        cid = top_chunk.get("chunk_id", "chunk_0")
                        src_items.append(f"**Document**: `{fn}` • **Page**: `{pg}` • **Chunk**: `{cid}`")
                    
                    if tab_src != "N/A":
                        method = "DuckDB SQL" if "DuckDB" in str(tab_src) else "Precomputed JSON"
                        src_items.append(f"**Data Source**: `analytical_dataset.csv` • **Method**: `{method}`")
                    
                    if category.lower() in ["weather", "household", "hybrid"]:
                        src_items.append("📍 **Location**: `London, United Kingdom`")

                    if src_items:
                        st.markdown(f"""
                        <div class="source-box">
                            {" &nbsp;|&nbsp; ".join(src_items)}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption("No external document or tabular evidence required for this response.")

                    # 4. COMPACT PERFORMANCE METRICS
                    st.markdown("### ⚡ PERFORMANCE & LLM")
                    perf1, perf2, perf3, perf4, perf5 = st.columns(5)
                    perf1.metric("⚡ Router", f"{router_lat} ms")
                    perf2.metric("🔎 Retrieval", f"{retrieval_lat} ms")
                    perf3.metric("🧠 LLM", f"{llm_lat} ms")
                    perf4.metric("⏱️ Total", f"{total_lat} ms")
                    perf5.metric("🤖 LLM Engine", f"{provider}")

                    st.caption(f"Model: `{model_name}`")

                    st.markdown("---")

                    # 5. OPTIONAL "VIEW EVIDENCE" (Collapsed by default)
                    with st.expander("🔍 View Evidence", expanded=False):
                        if retrieved_chunks:
                            st.markdown("##### 📄 Document Chunks (Sorted by Cosine Similarity Descending)")
                            sorted_chunks = sorted(retrieved_chunks, key=lambda x: (x.get("similarity_score") or 0.0), reverse=True)
                            for idx, chunk in enumerate(sorted_chunks, 1):
                                sim = chunk.get("similarity_score") or 0.0
                                cid = chunk.get("chunk_id", f"chunk_{idx}")
                                meta = chunk.get("metadata") or {}
                                fn = meta.get("file_name", "energy.pdf")
                                pg = meta.get("page", 1)
                                text = chunk.get("content", "")
                                
                                st.markdown(f"""
                                <div class="chunk-box">
                                    <b>Source:</b> {fn} &nbsp;|&nbsp; <b>Page:</b> {pg} &nbsp;|&nbsp; <b>Chunk:</b> {cid} &nbsp;|&nbsp; <b>Cosine Similarity:</b> {sim:.4f}<br>
                                    <div style="color: #cbd5e1; margin-top: 4px; font-size: 0.88rem;">"{text}"</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if tab_src != "N/A":
                            st.markdown("##### 📊 Tabular Analytics Evidence")
                            st.markdown(f"- **Source**: `{tab_src}`")
                            st.markdown(f"- **Retrieval Latency**: `{tab_lat} ms`")

            except Exception as e:
                st.error(f"An unexpected error occurred while executing the query: {e}")
