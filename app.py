import streamlit as st
import sqlite3
import hashlib
import ai as aipy
import pandas as pd  # temporary
# from cvr_analysis import CvrBusiness
from cvr_analysis_1 import CvrBusiness
from cvr_analysis_1 import cols_to_drop

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


_, col2, _ = st.columns([1, 2, 1])  # USED FOR SIGNIN AND LOGIN

# Function to create the main app


def main_app():

    cvr_business = CvrBusiness()

    @st.cache_data
    def load_data():
        data = cvr_business.merge_tables()  # remember to adjust
        # data['cvr'] = data['cvr'].astype(str)  # temporary
        return data

    # LOADS DATA
    data = load_data()
    data = data.drop(columns=cols_to_drop, axis=1)  # updated change

    _, colB, _ = st.columns(3, gap='small')
    with colB:
        st.title('Benchmark App📊')

    ######################## side bar #################################
    with st.sidebar:

        # User Input
        st.subheader('👤 User Inputs')
        cvr_num1 = st.text_input('Enter CVR 1', help='eg 25862716')
        cvr_num2 = st.text_input('Enter CVR 2', help='eg 10036127')
        # year_emp = st.text_input('Enter Year', help='Works with Employee plot')

        st.title('🔍 Filters')

        # Select a filter for merged data -- uses analyze business
        filters = ['low_debt', 'declining', 'profitable']
        select_filter = st.multiselect('Add Filter', filters)

        # Select metric to use
        metrics_to_analyze = ['', 'revenue',
                              'external_expenses', 'profit_loss']
        select_metric = st.selectbox(
            'Select Business Metric', metrics_to_analyze, help='This is used with compare company metric')

        # Select Plots to show
        st.subheader('Trend Analysis 📈')
        plot_1 = st.selectbox(
            'Select Plot', ['', 'compare companies profit', 'compare company metric'])

        st.subheader('Comparative Analysis ⚖️')
        plot_2 = st.selectbox('Select Plot 2', ['', 'compare roa'])

        st.subheader('Financial Health Indicators 💊')
        plot_3 = st.selectbox('Select Plot 3', ['', 'compare current ratio (single plot)',
                                                'compare current ratio', 'compare solvency ratio side_by_side',
                                                'compare solvency ratio combined'])

        st.subheader('Correlation  Analysis 📈📉')
        plot_4 = st.selectbox(
            'Select Plot 4', ['', 'compare revenue profit_loss'])

        st.subheader('Benchmarking  Analysis 📊🏋🏾‍♂️')
        plot_5 = st.selectbox(
            'Select Plot 5', ['', 'compare total employee count'])

        ############################# ai ##############################
        json_data = aipy.load_json()
        # gets company names
        companies_name = [company['company_name'].capitalize()
                          for company in json_data]
        companies_name.insert(0, '')

        # Business overview
        st.subheader('Business Overview',
                     help='Select a company to view its business overview')

        # Initialize a session state variable if it doesn't exist
        if 'selected_option' not in st.session_state:
            st.session_state['selected_option'] = None

        # Create a select box
        selected_company = st.selectbox("Choose an option:", companies_name)

        # Create a button
        if st.button("Confirm Selection"):
            # Store the selection in the session state when the button is clicked
            st.session_state['selected_option'] = selected_company

        # Display the stored selection
        if st.session_state['selected_option'] is not None:
            st.write(
                f"You have selected: {st.session_state['selected_option']}")

    ####################  Exit Slider  #############################

    # Get cvr
    cvr_list = [cvr_num1, cvr_num2]

    # Get filered data
    st.session_state['filter_selected'] = None
    if select_filter:
        with st.spinner('Filtering data...'):
            cvrs_filtered = cvr_business.analyze_companies(data, select_filter)
            filtered_d = cvr_business.apply_filter(cvrs_filtered, data)
            st.session_state['filter_selected'] = True

    # Select Metric
    st.session_state['metric_selected'] = None
    if select_metric:
        selected_metric = select_metric
        st.session_state['metric_selected'] = True

    ### SETS is_plotted to None --> for markdown ##
    st.session_state['is_plotted'] = None

    # Trend Analysis
    if plot_1:
        if 'compare companies profit' in plot_1:
            if st.session_state['filter_selected']:
                fig_1 = cvr_business.compare_companies_profit(
                    cvr_list, filtered_d)
            else:
                fig_1 = cvr_business.compare_companies_profit(cvr_list, data)
        else:
            if st.session_state['filter_selected']:
                if st.session_state['metric_selected']:
                    fig_1 = cvr_business.compare_company_metric(
                        filtered_d, cvr_list, selected_metric)
                else:
                    fig_1 = cvr_business.compare_company_metric(data, cvr_list)
            else:
                if st.session_state['metric_selected']:
                    fig_1 = cvr_business.compare_company_metric(
                        data, cvr_list, selected_metric)
                else:
                    fig_1 = cvr_business.compare_company_metric(data, cvr_list)
        st.session_state['is_plotted'] = True

    ######### Comparative Analysis ⚖️ #################
    if plot_2:
        if 'compare roa' in plot_2:
            if st.session_state['filter_selected']:
                fig_2 = cvr_business.compare_roa(filtered_d, cvr_list)
            else:
                fig_2 = cvr_business.compare_roa(data, cvr_list)
        st.session_state['is_plotted'] = True

    ######### Financial Health Indicators 💊 #################
    if plot_3:
        if 'compare current ratio (single plot)' in plot_3:
            if st.session_state['filter_selected']:
                fig_3 = cvr_business.compare_current_ratio_single_plot(
                    filtered_d, cvr_list)
            else:
                fig_3 = cvr_business.compare_current_ratio_single_plot(
                    data, cvr_list)
        elif 'compare current ratio' in plot_3:
            if st.session_state['filter_selected']:
                fig_3 = cvr_business.compare_current_ratio(
                    filtered_d, cvr_list)
            else:
                fig_3 = cvr_business.compare_current_ratio(data, cvr_list)
        elif 'compare solvency ratio side_by_side' in plot_3:
            if st.session_state['filter_selected']:
                fig_3 = cvr_business.compare_solvency_ratio_side_by_side(
                    filtered_d, cvr_list)
            else:
                fig_3 = cvr_business.compare_solvency_ratio_side_by_side(
                    data, cvr_list)
        elif 'compare solvency ratio combined' in plot_3:
            if st.session_state['filter_selected']:
                fig_3 = cvr_business.compare_solvency_ratio_combined(
                    filtered_d, cvr_list)
            else:
                fig_3 = cvr_business.compare_solvency_ratio_combined(
                    data, cvr_list)
        st.session_state['is_plotted'] = True

    ######### Correlation  Analysis 📈📉#################
    if plot_4:
        if 'compare revenue profit_loss' in plot_4:
            if st.session_state['filter_selected']:
                fig_4 = cvr_business.compare_revenue_profit_loss(
                    filtered_d, cvr_list)
            else:
                fig_4 = cvr_business.compare_revenue_profit_loss(
                    data, cvr_list)
        st.session_state['is_plotted'] = True

    ######### Benchmarking  Analysis 📊🏋🏾‍♂️ #################
    if plot_5:
        if 'compare total employee count' in plot_5:  # compare revenue profit_loss'
            if st.session_state['filter_selected']:
                fig_5 = cvr_business.compare_total_employee_count(
                    filtered_d, cvr_list)
            else:
                fig_5 = cvr_business.compare_total_employee_count(
                    data, cvr_list)
        st.session_state['is_plotted'] = True

    # COLUMNS TO SPLIT THE PAGE
    a = st.columns((0.5, 2, 0.5), gap='small')
    b = st.columns((0.5, 2, 0.5), gap='small')
    c = st.columns((0.5, 2, 0.5), gap='small')
    d = st.columns((0.5, 2, 0.5), gap='small')
    e = st.columns((0.5, 2, 0.5), gap='small')
    f = st.columns((0.5, 2, 0.5), gap='small')
    ########## USING COLUMN TO PLOT CHARTS ####################
    try:
        if any(data['cvr'].isin(cvr_list)) or any(filtered_d['cvr'].isin(cvr_list)):
            a[1].pyplot(fig_1)
    except:
        pass
    try:
        if any(data['cvr'].isin(cvr_list)) or any(filtered_d['cvr'].isin(cvr_list)):
            b[1].pyplot(fig_2)
    except:
        pass
    try:
        if any(data['cvr'].isin(cvr_list)) or any(filtered_d['cvr'].isin(cvr_list)):
            c[1].pyplot(fig_3)
    except:
        pass
    try:
        if any(data['cvr'].isin(cvr_list)) or any(filtered_d['cvr'].isin(cvr_list)):
            d[1].pyplot(fig_4)
    except:
        pass
    try:
        if any(data['cvr'].isin(cvr_list)) or any(filtered_d['cvr'].isin(cvr_list)):
            e[1].pyplot(fig_5)
    except:
        pass

    ############### Business overview display ################
    if st.session_state['is_plotted']:
        if selected_company and st.session_state['selected_option']:
            description = aipy.get_company_description(
                json_data, selected_company.lower())
            mrkd = aipy.get_markdown_description(description)
            try:
                f[1].markdown(mrkd)  # mrkd
            except:
                pass
    else:
        if selected_company and st.session_state['selected_option']:
            description = aipy.get_company_description(
                json_data, selected_company.lower())
            mrkd = aipy.get_markdown_description(description)
            try:
                st.markdown(mrkd)
            except:
                pass


############################ AUTHENTICATION ##################################

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
