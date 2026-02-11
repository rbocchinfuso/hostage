import random
import time

import streamlit as st

# --- CONFIGURATION & MOCK RAG DATA ---
# In a production app, these would be retrieved from a Vector DB based on user input.
SALES_PLAYBOOK = {
    "objections": "If the player mentions 'budget', remind them of the ROI of $5M over 3 years.",
    "tactics": "Effective negotiators use 'anchoring' and 'active listening'. Reject aggressive demands.",
    "deal_terms": "Minimum price is $2.1M. Delivery must be within 6 months.",
}


def get_rag_context(user_input):
    """Simulates RAG retrieval based on keywords in user input."""
    context = ""
    if "budget" in user_input.lower() or "price" in user_input.lower():
        context += SALES_PLAYBOOK["objections"]
    if "when" in user_input.lower() or "delivery" in user_input.lower():
        context += SALES_PLAYBOOK["deal_terms"]
    return context if context else SALES_PLAYBOOK["tactics"]


# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="The $10M Closer", page_icon="💼")
st.title("💼 The $10M Purchase Order Challenge")
st.markdown("""
**The Mission:** You have **120 seconds** to convince the AI CFO to sign a multi-million dollar PO.
If you are too aggressive, the deal is rescinded. If you are too weak, the deal is lost.
""")

# --- SESSION STATE INITIALIZATION ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "deal_status" not in st.session_state:
    st.session_state.deal_status = "Pending"

# --- TIMER LOGIC ---
timer_placeholder = st.sidebar.empty()

if st.sidebar.button("🚀 Start Negotiation"):
    st.session_state.start_time = time.time()
    st.session_state.game_over = False
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "I'm listening. Why should I sign this $5,000,000 order today?",
        }
    ]
    st.rerun()

# --- GAME LOOP ---
if st.session_state.start_time and not st.session_state.game_over:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 120 - int(elapsed))

    timer_placeholder.metric("Time Remaining", f"{remaining}s")

    if remaining <= 0:
        st.session_state.game_over = True
        st.session_state.deal_status = "RESCINDED (Out of Time)"
        st.error("⏰ Time is up! The CFO walked out of the room.")

    # --- CHAT INTERFACE ---
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your negotiation tactic..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # RAG Context Retrieval
        context = get_rag_context(prompt)

        # --- MOCK AI DECISION LOGIC ---
        # In a real app, send 'context + prompt' to OpenAI/Gemini
        if "discount" in prompt.lower() and "50%" in prompt.lower():
            response = (
                "That is insulting. I'm considering rescinding this offer entirely."
            )
            sentiment = "bad"
        elif "value" in prompt.lower() or "roi" in prompt.lower():
            response = "I like your focus on value. Tell me more about the implementation timeline."
            sentiment = "good"
        else:
            response = "I've heard this before. Give me a hard reason to sign."
            sentiment = "neutral"

        # Simulate "Winning" condition
        if "sign" in prompt.lower() and sentiment == "good":
            st.session_state.game_over = True
            st.session_state.deal_status = "ISSUED ✅"
            response = "You've convinced me. Consider the PO issued. Great negotiating."

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

        if st.session_state.game_over:
            st.rerun()

# --- END GAME SCREEN ---
if st.session_state.game_over:
    st.divider()
    if "ISSUED" in st.session_state.deal_status:
        st.balloons()
        st.success(f"FINAL DECISION: {st.session_state.deal_status}")
    else:
        st.error(f"FINAL DECISION: {st.session_state.deal_status}")

    if st.button("Try Again"):
        st.session_state.start_time = None
        st.rerun()
