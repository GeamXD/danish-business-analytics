import streamlit as st
import streamlit_shadcn_ui as ui
import hmac


st.set_page_config(page_title="Streamlit Shadcn UI",
                   page_icon=":shark:", layout="wide")

# Create columns with desired width proportions
_, col2, _ = st.columns([1, 2, 1])

###################### LOGIN ########################################


def check_password():
    # Returns `True` if the user had a correct password.

    def login_form():
        # Place the form in the middle column

        with col2:
            # Form with widgets to collect user information
            with st.form("Credentials"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        # Checks whether a password entered by the user is correct
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            # Don't store the username or password.
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

####################### Main Streamlit ##################################
st.write('welcome to the app')
