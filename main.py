import streamlit as st
from modules import summary #, first_step, second_step, third_step, offline_familiarisation_steps, further_steps, advanced_steps

# flashcard data
flashcards = [
    {"question": "What is the capital of Sweden?", "answer": "Stockholm"},
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is the capital of Italy?", "answer": "Rome"},
    # add more flashcards as needed
]

def run_flashcards():
    card = st.session_state.card
    show_answer = st.session_state.show_answer

    if show_answer:
        st.subheader(card["answer"])
        if st.button("Next"):
            st.session_state.card = flashcards[(flashcards.index(card) + 1) % len(flashcards)]
            st.session_state.show_answer = False
            st.experimental_rerun()
    else:
        st.subheader(card["question"])
        if st.button("Show Answer"):
            st.session_state.show_answer = True
            st.experimental_rerun()

def main():
    st.sidebar.title('Course Modules')
    modules = {
        'Summary': summary,
        #'First Step': first_step,
        #'Second Step': second_step,
        #'Third Step': third_step,
        #'Offline Familiarisation Steps': offline_familiarisation_steps,
        #'Further Steps': further_steps,
        #'Advanced Steps': advanced_steps
    }
    if "module_choice" not in st.session_state:
        st.session_state.module_choice = "Summary"

    module_choice = st.sidebar.selectbox("Choose a module", list(modules.keys()), index=list(modules.keys()).index(st.session_state.module_choice))

    # if the module choice changes, update the session state and set mode back to 'module'
    if module_choice != st.session_state.module_choice:
        st.session_state.module_choice = module_choice
        st.session_state.mode = "module"
    
    # add flashcard tab
    flashcard_tab = st.sidebar.button("Flashcards")

    if "mode" not in st.session_state:
        st.session_state.mode = "module"

    if flashcard_tab:
        st.session_state.mode = "flashcards"
        st.session_state.card = flashcards[0]
        st.session_state.show_answer = False

    if st.session_state.mode == "flashcards":
        run_flashcards()
    else:
        # run the module corresponding to module_choice
        modules[module_choice].run()

if __name__ == "__main__":
    main()
