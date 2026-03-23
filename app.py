import streamlit as st
from dataclasses import dataclass

st.set_page_config(
    page_title="Learning Lab Clinical Communication Demo",
    page_icon="🧪",
    layout="wide",
)

SCENARIOS = {
    "The De-escalation Dance": {
        "title": "The De-escalation Dance",
        "learner_role": "Learner directing a clinician during a tense Emergency Department encounter",
        "patient_role": "Patient waiting in the Emergency Department for six hours",
        "opening_patient": "I've been sitting here for hours. Nobody is telling me anything. I feel awful, and this is ridiculous.",
        "goal": "Use verbal de-escalation while noticing this may be a medical emergency, not only a behavioral one.",
        "hidden_clue": "The patient is shaky, sweaty, and increasingly agitated. This may be hypoglycemia or a medication-related reaction.",
    },
    "The Swiss Cheese Safety Catch": {
        "title": "The Swiss Cheese Safety Catch",
        "learner_role": "Learner directing a clinician during a high-risk safety check",
        "patient_role": "Patient preparing for surgery or a high-risk medication",
        "opening_patient": "I just want to make sure this is right. My bracelet looks a little off, and I think I might have a latex allergy.",
        "goal": "Spot cumulative risk and help the clinician halt the process before a preventable safety event occurs.",
        "hidden_clue": "There is a typo on the wristband, the dosage is near the upper limit, and the possible latex allergy is not in the chart.",
    },
}

DIRECTOR_MOVES = {
    "Reflect emotion": "It sounds like this has been overwhelming and exhausting.",
    "Ask permission": "Would it be okay if we take one step at a time together?",
    "Name uncertainty": "I don't know the full answer yet, but I want to be clear about what we do know and what we still need to check.",
    "Explore values": "What matters most to you right now as we figure out what is happening?",
    "Summarize + check": "Let me see if I have this right before we move forward.",
}

TONE_OPTIONS = ["Warm", "Neutral", "Challenging"]


@dataclass
class DemoState:
    trust: int = 45
    clarity: int = 40
    emotional_intensity: int = 60


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "demo" not in st.session_state:
        st.session_state.demo = DemoState()
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "active_scenario" not in st.session_state:
        st.session_state.active_scenario = list(SCENARIOS.keys())[0]
    if "last_vote" not in st.session_state:
        st.session_state.last_vote = None


def reset_chat(scenario_name: str):
    scenario = SCENARIOS[scenario_name]
    st.session_state.messages = [
        {
            "speaker": "System",
            "content": f"""**Scenario:** {scenario['title']}

**Mode:** Director Mode
**You are:** {scenario['learner_role']}
**Patient:** {scenario['patient_role']}

**Goal:** {scenario['goal']}

**How it works:** The patient and clinician are already mid-visit. You are directing the clinician by choosing short communication moves that change tone and trajectory.""",
        },
        {
            "speaker": "Patient",
            "content": scenario["opening_patient"],
        },
    ]
    st.session_state.demo = DemoState()
    st.session_state.initialized = True
    st.session_state.active_scenario = scenario_name
    st.session_state.last_vote = None


def interpret_move(move: str) -> str:
    return DIRECTOR_MOVES.get(move, move)


def literal_and_impact(text: str):
    lowered = text.lower()

    if "sounds like" in lowered or "overwhelming" in lowered or "exhausting" in lowered:
        impact = "Likely lands as empathy and emotional validation."
    elif "would it be okay" in lowered:
        impact = "Likely lands as respectful and collaborative."
    elif "don't know" in lowered or "still need to check" in lowered:
        impact = "Likely lands as transparency, though it may also raise anxiety if not paired with reassurance."
    elif "what matters most" in lowered:
        impact = "Likely lands as curiosity about the patient's priorities and values."
    elif "let me see if i have this right" in lowered:
        impact = "Likely lands as alignment and careful listening."
    else:
        impact = "Could land as efficient, but may need more warmth to feel empathic."

    return text, impact


def simulate_clinician_response(user_text: str, tone: str) -> str:
    lowered = user_text.lower()

    if tone == "Warm":
        prefix = "I want to slow down and be with you in this for a moment. "
    elif tone == "Challenging":
        prefix = "Let's focus carefully on what matters right now. "
    else:
        prefix = "Let's take this step by step. "

    if "sounds like" in lowered or "overwhelming" in lowered:
        return prefix + "It sounds like this has been exhausting, and I can see you're really frustrated."
    if "would it be okay" in lowered:
        return prefix + "Would it be okay if I ask a couple of quick questions so I can understand what's changing for you?"
    if "don't know" in lowered or "need to check" in lowered:
        return prefix + "I don't want to guess. I want to check what's going on and tell you clearly what I find."
    if "what matters most" in lowered:
        return prefix + "Before we jump ahead, what feels most important for you right now?"
    if "let me see if i have this right" in lowered:
        return prefix + "Let me make sure I have this right before we keep going."

    return prefix + user_text


def simulate_patient_response(user_text: str, scenario_name: str) -> str:
    lowered = user_text.lower()

    if scenario_name == "The De-escalation Dance":
        if "overwhelming" in lowered or "exhausting" in lowered:
            return "Yeah. Exactly. I've been trying to hold it together, but I feel shaky and weird."
        if "okay if i ask" in lowered or "quick questions" in lowered:
            return "Fine. But something feels really off. I'm sweaty and lightheaded."
        if "don't want to guess" in lowered or "check what's going on" in lowered:
            return "Thank you. I don't feel right. This feels different than just being upset."
        if "what feels most important" in lowered:
            return "I need someone to actually notice that I feel physically wrong, not just angry."
        if "have this right" in lowered:
            return "Yes. I've waited forever, and now I feel shaky, sweaty, and like something is wrong."
        return "I'm still upset, but at least you're actually listening now."

    if "overwhelming" in lowered or "exhausting" in lowered:
        return "Yes, and I don't want something small to turn into a big mistake."
    if "okay if i ask" in lowered or "quick questions" in lowered:
        return "Please. I just noticed the bracelet typo and remembered the possible latex issue."
    if "don't want to guess" in lowered or "check what's going on" in lowered:
        return "Good. I would feel better if someone paused and checked everything carefully."
    if "what feels most important" in lowered:
        return "I want to know the right person, the right dose, and no allergy surprises."
    if "have this right" in lowered:
        return "Yes. The bracelet looks off, the allergy question feels unresolved, and I want to be sure this is safe."
    return "Something feels slightly off, and I don't want to ignore it."


def update_demo_state(user_text: str, move: str):
    text = user_text.lower()

    if any(word in text for word in ["sorry", "hear", "understand", "hard", "worry", "sounds like"]):
        st.session_state.demo.trust = min(100, st.session_state.demo.trust + 8)
        st.session_state.demo.emotional_intensity = max(0, st.session_state.demo.emotional_intensity - 4)

    if any(word in text for word in ["plan", "next", "step", "option", "recommend", "check"]):
        st.session_state.demo.clarity = min(100, st.session_state.demo.clarity + 10)

    if any(word in text for word in ["no", "but", "actually"]):
        st.session_state.demo.emotional_intensity = min(100, st.session_state.demo.emotional_intensity + 5)

    if move == "Reflect emotion":
        st.session_state.demo.trust = min(100, st.session_state.demo.trust + 5)
    elif move == "Ask permission":
        st.session_state.demo.emotional_intensity = max(0, st.session_state.demo.emotional_intensity - 3)
    elif move == "Name uncertainty":
        st.session_state.demo.clarity = min(100, st.session_state.demo.clarity + 6)
    elif move == "Explore values":
        st.session_state.demo.trust = min(100, st.session_state.demo.trust + 4)
    elif move == "Summarize + check":
        st.session_state.demo.clarity = min(100, st.session_state.demo.clarity + 8)


def render_sidebar():
    st.sidebar.title("Demo Controls")

    scenario_name = st.sidebar.selectbox(
        "Choose a clinical scenario",
        list(SCENARIOS.keys()),
        index=list(SCENARIOS.keys()).index(st.session_state.active_scenario),
    )

    if st.sidebar.button("Load scenario", width="stretch"):
        reset_chat(scenario_name)
        st.rerun()

    st.sidebar.markdown("### Demo mode")
    demo_mode = st.sidebar.radio(
        "Choose interaction mode",
        ["Director Mode", "What You See vs What You Heard"],
        index=0,
    )

    tone = st.sidebar.radio("Clinician tone", TONE_OPTIONS, index=0)

    move = st.sidebar.selectbox(
        "Choose a communication move",
        list(DIRECTOR_MOVES.keys()),
    )

    move_notes = {
        "Reflect emotion": "Use language like 'It sounds like...' to lower the temperature and show understanding.",
        "Ask permission": "Use language like 'Would it be okay if we...?' to preserve autonomy and reduce friction.",
        "Name uncertainty": "Use honest clarity when certainty is not available yet.",
        "Explore values": "Surface what matters most before rushing into solutions.",
        "Summarize + check": "Pause and align before moving forward.",
    }

    st.sidebar.markdown("### Move notes")
    st.sidebar.info(move_notes[move])

    scenario = SCENARIOS[st.session_state.active_scenario]
    st.sidebar.markdown("### Hidden clue")
    st.sidebar.caption(scenario["hidden_clue"])

    st.sidebar.markdown("### Learner state")
    st.sidebar.write(f"Trust: {st.session_state.demo.trust}")
    st.sidebar.progress(st.session_state.demo.trust / 100)
    st.sidebar.write(f"Clarity: {st.session_state.demo.clarity}")
    st.sidebar.progress(st.session_state.demo.clarity / 100)
    st.sidebar.write(f"Emotional intensity: {st.session_state.demo.emotional_intensity}")
    st.sidebar.progress(st.session_state.demo.emotional_intensity / 100)

    facilitator_mode = st.sidebar.toggle("Show facilitator panel", value=True)

    return tone, move, facilitator_mode, demo_mode


def render_facilitator_panel(demo_mode: str):
    with st.expander("Facilitator panel", expanded=True):
        st.markdown(
            """
Use this prototype to demonstrate:

- how the learner can steer a clinical encounter without fully taking over the clinician role
- how short communication moves can visibly change trust, clarity, and emotional intensity
- how communication training becomes more concrete when subtext is made visible
"""
        )

        if demo_mode == "Director Mode":
            st.markdown(
                """
**Director Mode**
The learner acts like a communication director, nudging the clinician with short interventions that redirect the scene.
"""
            )
        else:
            st.markdown(
                """
**What You See vs What You Heard**
After the learner speaks, the app reveals:
- the literal content
- the likely emotional impact

This makes subtext visible and sets up replay, revision, and discussion.
"""
            )


def add_director_move(move_name: str, tone: str):
    selected_text = interpret_move(move_name)
    st.session_state.messages.append({"speaker": "Director", "content": selected_text})

    clinician_line = simulate_clinician_response(selected_text, tone)
    st.session_state.messages.append({"speaker": "Clinician", "content": clinician_line})

    patient_line = simulate_patient_response(clinician_line, st.session_state.active_scenario)
    st.session_state.messages.append({"speaker": "Patient", "content": patient_line})

    update_demo_state(selected_text, move_name)


def main():
    init_state()

    if not st.session_state.initialized:
        reset_chat(st.session_state.active_scenario)

    tone, move, facilitator_mode, demo_mode = render_sidebar()
    scenario = SCENARIOS[st.session_state.active_scenario]

    st.title("🧪 Learning Lab Clinical Communication Demo")
    st.caption("Streamlit prototype for in-person and online Learning Lab demos")

    header_col1, header_col2 = st.columns([1.5, 1])

    with header_col1:
        st.subheader(scenario["title"])
        st.write(f"**Mode:** {demo_mode}")
        st.write(f"**Learner role:** {scenario['learner_role']}")
        st.write(f"**Teaching goal:** {scenario['goal']}")

    with header_col2:
        st.metric("Trust", st.session_state.demo.trust)
        st.metric("Clarity", st.session_state.demo.clarity)
        st.metric("Emotional intensity", st.session_state.demo.emotional_intensity)

    if facilitator_mode:
        render_facilitator_panel(demo_mode)

    st.markdown("---")

    scene_col, insight_col = st.columns([1.6, 1])

    with scene_col:
        st.markdown("### Live scene")
        for message in st.session_state.messages:
            speaker = message["speaker"]
            content = message["content"]

            if speaker == "System":
                with st.chat_message("assistant"):
                    st.markdown(content)
            elif speaker == "Patient":
                with st.chat_message("assistant"):
                    st.markdown(f"**Patient:** {content}")
            elif speaker == "Clinician":
                with st.chat_message("assistant"):
                    st.markdown(f"**Clinician:** {content}")
            else:
                with st.chat_message("user"):
                    st.markdown(f"**Director:** {content}")

        st.markdown("### Quick move buttons")
        quick_cols = st.columns(5)

        for col, quick_move in zip(quick_cols, DIRECTOR_MOVES.keys()):
            with col:
                if st.button(quick_move):
                    add_director_move(quick_move, tone)
                    st.rerun()

        prompt = st.chat_input("Type your own director intervention, or use a quick move above...")

        if prompt:
            st.session_state.messages.append({"speaker": "Director", "content": prompt})
            clinician_line = simulate_clinician_response(prompt, tone)
            st.session_state.messages.append({"speaker": "Clinician", "content": clinician_line})
            patient_line = simulate_patient_response(clinician_line, st.session_state.active_scenario)
            st.session_state.messages.append({"speaker": "Patient", "content": patient_line})
            update_demo_state(prompt, move)
            st.rerun()

    with insight_col:
        st.markdown("### Insight panel")

        if demo_mode == "What You See vs What You Heard":
            last_director_message = None
            for msg in reversed(st.session_state.messages):
                if msg["speaker"] == "Director":
                    last_director_message = msg["content"]
                    break

            if last_director_message:
                literal, impact = literal_and_impact(last_director_message)

                st.markdown("**What you said**")
                st.info(literal)

                st.markdown("**Likely impact**")
                st.warning(impact)

                st.markdown("**Audience vote**")
                vote_col1, vote_col2 = st.columns(2)
                with vote_col1:
                    if st.button("Landed as empathy"):
                        st.session_state.last_vote = "Audience vote: empathy"
                        st.rerun()
                with vote_col2:
                    if st.button("Landed as efficiency"):
                        st.session_state.last_vote = "Audience vote: efficiency"
                        st.rerun()

                if st.session_state.last_vote:
                    st.success(st.session_state.last_vote)
            else:
                st.caption("Make a director move to reveal the split-screen insight.")
        else:
            st.markdown("**Director mode focus**")
            st.write("Use the move buttons to nudge the clinician and watch how the patient response changes.")
            st.write("This is useful for live workshop facilitation because the learner shapes the visit without needing to improvise every line.")

        st.markdown("---")
        st.markdown("**Messages in scene**")
        st.write(len(st.session_state.messages))


if __name__ == "__main__":
    main()