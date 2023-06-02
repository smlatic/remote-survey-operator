import streamlit as st
from modules import summary #, first_step, second_step, third_step, offline_familiarisation_steps, further_steps, advanced_steps

def main():
    st.sidebar.title("Introduction to Remote Surveying: Becoming a Remote Survey Operator")
    modules = {
        'Summary': summary,
        #'First Step': first_step,
        #'Second Step': second_step,
        #'Third Step': third_step,
        #'Offline Familiarisation Steps': offline_familiarisation_steps,
        #'Further Steps': further_steps,
        #'Advanced Steps': advanced_steps,
    }
    choice = st.sidebar.selectbox("Choose Module", list(modules.keys()))

    module = modules[choice]
    module.run()

if __name__ == "__main__":
    main()
