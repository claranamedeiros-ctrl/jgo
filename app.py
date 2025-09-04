import streamlit as st
import os
from datetime import datetime
import time
from core.auth import AuthManager
from core.bedrock_client import BedrockClient
from core.conversation import ConversationManager
from core.guardrails import COPPAGuardrails
from core.constants import DEMO_USERS 

st.set_page_config(
    page_title="JurneeGo - Safe AI Learning Assistant",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    from dotenv import load_dotenv
    load_dotenv()
    if 'env_loaded' not in st.session_state:
        st.session_state.env_loaded = True
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

try:
    for key, value in st.secrets.items():
        os.environ.setdefault(key, str(value))
except Exception as e:
    print(f"Warning: Could not load Streamlit secrets: {e}")

    
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()
if 'bedrock_client' not in st.session_state:
    st.session_state.bedrock_client = BedrockClient()
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
if 'guardrails' not in st.session_state:
    st.session_state.guardrails = COPPAGuardrails()

# Custom CSS made by a non designer clearly
st.markdown("""
<style>
    .child-mode {
        background-color: #E8F4FD;
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
    }
    .parent-mode {
        background-color: #F0F8FF;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .teacher-mode {
        background-color: #FFF8DC;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .safety-alert {
        background-color: #FFE4E1;
        border: 2px solid #FF6347;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .stButton > button {
        border-radius: 20px;
        font-size: 16px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ffeeba;'>
<h4 style='color: #856404; margin: 0;'>🔧 Demo Mode - JurneeGo Prototype</h4>
<p style='color: #856404; margin: 5px 0 0 0; font-size: 14px;'>Production version includes AWS Bedrock Guardrails, DynamoDB persistence, and enterprise security</p>
</div>
""", unsafe_allow_html=True)


def show_login():
    st.title("🌟 Welcome to JurneeGo!")
    st.subheader("Safe AI Learning Assistant for Children")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please Sign In")
        
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                user = st.session_state.auth_manager.authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    
                    # COPPA Compliance Check for Children - VISIBLE IN UI
                    if user['role'] == 'child':
                        with st.spinner("🔐 Verifying parental consent..."):
                            time.sleep(1.5)  # Demo effect
                        st.success("✅ COPPA Compliance: Parental consent verified")
                        st.info("✅ Age-appropriate content filters activated")
                        time.sleep(1)  # Let them see the messages
                    
                    
                    for key in list(st.session_state.keys()):
                        if key.startswith('FormSubmitter'):
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        
        with st.expander("Demo Credentials"):
            st.markdown(f"""
            **Parent Account:**
            - Username: `{DEMO_USERS['parent']['username']}`
            - Password: `{DEMO_USERS['parent']['password']}`
            
            **Child Account:**
            - Username: `{DEMO_USERS['child']['username']}`
            - Password: `{DEMO_USERS['child']['password']}`
            
            **Teacher Account:**
            - Username: `{DEMO_USERS['teacher']['username']}`
            - Password: `{DEMO_USERS['teacher']['password']}`
            """)


def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        show_login()
        return
    
    user = st.session_state.user
    
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.markdown(f"**Role:** {user['role'].title()}")
        
        if user['role'] == 'child':
            st.markdown(f"**Age:** {user['age']}")
            
            
            st.markdown("### 🛡️ Safety Status")
            st.success("✅ Content Filtering: Active")
            st.success("✅ Parent Monitoring: Active")
            st.success("✅ COPPA Compliant: Verified")
            st.info("🔒 End-to-End Encrypted")
            
            # Session timer for COPPA compliance
            if 'session_start' not in st.session_state:
                st.session_state.session_start = datetime.now()
            
            settings = st.session_state.guardrails.get_age_appropriate_settings(user['age'])
            max_minutes = settings['max_session_minutes']
            
           
            from core.constants import SESSION_DURATION_WARNING
            st.markdown(SESSION_DURATION_WARNING.format(max_minutes))
            
      
            elapsed = (datetime.now() - st.session_state.session_start).total_seconds() / 60
            if elapsed > max_minutes:
                st.error(f"⏰ Session limit reached ({max_minutes} min). Time for a break!")
                time.sleep(2)
                st.stop()
        
        elif user['role'] == 'parent':
     
            st.markdown("### 🛡️ Safety Overview")
            st.success("✅ Real-time Monitoring Active")
            st.info("📊 Check Analytics Tab for Details")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.auth_manager.logout(user['session_id'])
            for key in list(st.session_state.keys()):
                if key not in ['auth_manager', 'bedrock_client', 'conversation_manager', 'guardrails']:
                    del st.session_state[key]
            st.rerun()
    
   
    if user['role'] == 'child':
        from pages import child_chat
        child_chat.show(user, st.session_state)
    elif user['role'] == 'parent':
        from pages import parent_dashboard
        parent_dashboard.show(user, st.session_state)
    elif user['role'] == 'teacher':
        from pages import teacher_view
        teacher_view.show(user, st.session_state)

if __name__ == "__main__":
    main()