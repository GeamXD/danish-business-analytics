import streamlit as st
import sqlite3
import hashlib
import ai as aipy
from cvr_analysis import CvrBusiness

st.set_page_config(
    page_title="Benchmark App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Function to create a new database connection


def get_connection():
    return sqlite3.connect('users.db', check_same_thread=False)

# Function to create the users table


def create_users_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.close()
    conn.close()


# Create the users table if it does not exist
create_users_table()

# Function to hash the password


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate the login


def validate_login(username, hashed_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password =?',
              (username, hashed_password))
    result = c.fetchone()
    c.close()
    conn.close()
    return result is not None

# Function to insert a new user


def insert_user(username, hashed_password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username, password) VALUES (?,?)',
                  (username, hashed_password))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    finally:
        c.close()
        conn.close()
    return result

####################### APP LAYOUT ##################################


_, col2, _ = st.columns([1, 2, 1])

# Function to create the main app

def main_app():


    @st.cache_data
    def load_data():
        cvr_business = CvrBusiness()
        data = cvr_business.merge_tables()
        return data




    _, colB, _ = st.columns([1, 2, 1])
    with colB:
        st.markdown('#### Welcome to Benchmark App 📈⏱️📊')
    
    # data = load_data()
 



    ## side bar
    with st.sidebar:
        st.title('🔍 Filters')

        # Select a filter for merged data -- uses analyze business
        filters = ['low_debt', 'declining', 'profitable']
        select_filter = st.multiselect('Add Filter', filters)

        # Select Plots to show
        st.title('Trend Analysis')
        plot_1 = st.multiselect('Select Plot', ['compare companies profit','compare company metric'])
        # plot_2 = []

        st.title('Comparison Analysis')
        plot_3 = st.multiselect('Select Plot 2', ['compare roa' ])

        st.title('Financial Health Indicators')
        plot_4 = st.multiselect('Select Plot 3', ['compare current ratio (single plot)', 
        'compare current ratio', 'compare solvency ratio side_by_side', 
        'compare solvency ratio combined'])
        # plot_5 = []
        # plot_6 = []
        # plot_7 = []

        st.title('Correlation  Analysis')
        plot_8 = st.multiselect('Select Plot 4', ['compare revenue profit_loss'])
        
        st.title('Benchmarking  Analysis')
        plot_9 = st.multiselect('Select Plot 5', ['compare total employee count'])


        st.title('👤 User Inputs')
        cvr_num1 = st.text_input('Enter CVR_1')
        cvr_num2 = st.text_input('Enter CVR_2')

        # Last option at the bottom
        json_data = aipy.load_json()
        # gets company names
        companies_name = [company['company_name'] for company in json_data]
        companies_name.insert(0,'')
        selected_company = st.selectbox('Load Business Overview', companies_name)

        # gets company description
    # If company name is selected
    if selected_company:
        description = aipy.get_company_description(json_data, selected_company)
        mrkd = aipy.get_markdown_description(description)
        st.markdown(mrkd)
    
    # description = aipy.get_company_description(json_data, companies_name[0])
    # st.write(description)

    if select_filter:
        cvrs_filtered = cvr_business.analysis_choices(data, select_filter)
        filtered_d = cvr_business.apply_filter(cvrs_filtered, data)
    




####################### AUTHENTICATION ##################################

# Function to create the login form
def login_form():
    with col2:
        st.markdown(
            "<h2 style='text-align: center; color: #333333;'>Login</h2>", unsafe_allow_html=True)
        with st.form("Credentials"):
            username = st.text_input(
                "Username", key="username", placeholder="User Name", label_visibility='hidden')
            password = st.text_input(
                "Password", type="password", key="password", placeholder="Password", label_visibility='hidden')
            submit_button = st.form_submit_button("Log in")

            if submit_button and username and password:
                hashed_password = hash_password(password)
                if validate_login(username, hashed_password):
                    st.session_state["authenticated"] = True
                    st.success("🎉 Logged in successfully.")
                else:
                    st.error("😕 User not known or password incorrect")


# Function to create the sign up form
def sign_up_form():
    with col2:
        st.write('')
        st.write('')
        st.write('')
        st.markdown(
            "<h2 style='text-align: center; color: #333333;'>Sign Up</h2>", unsafe_allow_html=True)
        with st.form("Sign_up"):
            new_username = st.text_input(
                "New username", key="new_username", placeholder="Enter New User Name", label_visibility='hidden')
            new_password = st.text_input(
                "New password", type="password", key="new_password", placeholder="Enter New Password", label_visibility='hidden')
            submit_button = st.form_submit_button("Sign up")

            if submit_button and new_username and new_password:
                hashed_password = hash_password(new_password)
                if insert_user(new_username, hashed_password):
                    st.success("User created successfully.")
                else:
                    st.error("This username is already taken.")


if not st.session_state.get("authenticated"):
    login_form()
    sign_up_form()
else:
    main_app()
