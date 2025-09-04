import streamlit as st
from datetime import datetime
import time
import random
from core.constants import LEARNING_TIPS  # Import constants

def show(user, session_state):
    """Child chat interface with safety features using modern Streamlit chat components"""
    
    
    if 'current_conversation_id' not in st.session_state:
        conv_id = session_state.conversation_manager.create_conversation(
            user_id=user['id'],
            user_role='child',
            parent_id=user.get('parent_id')
        )
        st.session_state.current_conversation_id = conv_id
    
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi! I'm JurneeGo, your learning buddy! Ask me anything you're curious about!"
        })
    
    
    if 'safety_logs' not in st.session_state:
        st.session_state.safety_logs = []
    
    
    st.markdown(f"# 🌟 Hi {user['name'].split()[0]}! Let's Learn Together! 🎉")
    
    
    with st.sidebar:
        st.markdown("### 🎯 Fun Features")
        
        
        if st.session_state.safety_logs:
            st.markdown("### 🛡️ Safety Activity")
            for log in st.session_state.safety_logs[-3:]:  
                if 'CRITICAL' in log:
                    st.error(log)
                elif 'HIGH' in log:
                    st.warning(log)
                else:
                    st.info(log)
        
        
        if st.button("🧹 New Chat", use_container_width=True):
            
            st.session_state.messages = [{
                "role": "assistant",
                "content": "👋 Hi! Ready for a new adventure? What would you like to learn about?"
            }]
            
            
            new_conv_id = session_state.conversation_manager.create_conversation(
                user_id=user['id'],
                user_role='child',
                parent_id=user.get('parent_id')
            )
            st.session_state.current_conversation_id = new_conv_id
            
            
            if 'saved_questions' in st.session_state:
                st.session_state.saved_questions = []
            
            st.success("✨ New chat started! Ask me anything!")
        
        
        with st.expander("💾 Save for Later"):
            saved_question = st.text_area(
                "Write a question to save:",
                height=100,
                placeholder="What do you want to learn about later?",
                key="save_question_text"
            )
            if st.button("Save Question", key="save_btn"):
                if saved_question:
                    if 'saved_questions' not in st.session_state:
                        st.session_state.saved_questions = []
                    st.session_state.saved_questions.append({
                        'question': saved_question,
                        'timestamp': datetime.now().isoformat()
                    })
                    st.success("Question saved! ✅")
        
        
        if 'saved_questions' in st.session_state and st.session_state.saved_questions:
            st.markdown("### 📚 Saved Questions")
            for i, sq in enumerate(st.session_state.saved_questions[-3:]):  # Show last 3
                if st.button(f"{sq['question'][:30]}...", key=f"saved_{i}", use_container_width=True):
                    st.info("Copy this question to ask JurneeGo!")
                    st.code(sq['question'])
        
        
        st.markdown("### 💡 Learning Tip")
        st.info(random.choice(LEARNING_TIPS))
        
        
        st.markdown("### 🏆 Your Badges")
        message_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        
        if message_count >= 5:
            st.markdown("🌟 **Question Master** - Asked 5+ questions!")
        if message_count >= 10:
            st.markdown("🚀 **Super Learner** - Asked 10+ questions!")
        if message_count >= 20:
            st.markdown("🎓 **Knowledge Expert** - Asked 20+ questions!")
        
        
        st.markdown("### 😊 How are you feeling?")
        mood = st.radio(
            "Pick an emoji:",
            ["😊 Happy", "😐 Okay", "😢 Sad", "😟 Worried"],
            key="mood_check",
            label_visibility="collapsed"
        )
        
        if mood in ["😢 Sad", "😟 Worried"]:
            st.info("It's okay to feel this way. Would you like to talk to a grown-up?")
            if st.button("Yes, please", key="notify_parent"):
                st.success("We'll let your parent know you'd like to talk! 💙")
                
                log_entry = f"{datetime.now().strftime('%H:%M')} - Child requested parent support (Mood: {mood})"
                st.session_state.safety_logs.append(log_entry)
                
                session_state.conversation_manager.add_message(
                    st.session_state.current_conversation_id,
                    'system',
                    f"Child selected mood: {mood} and requested parent notification",
                    metadata={'type': 'mental_health_check', 'mood': mood}
                )
    
    
    chat_container = st.container()
    
    with chat_container:
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🧒" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
                
                
                if "reactions" in message and message["reactions"]:
                    reactions_str = " ".join(message["reactions"])
                    st.caption(f"Parent reactions: {reactions_str}")
                
                
                if "curator_notes" in message and message["curator_notes"]:
                    for note in message["curator_notes"]:
                        st.info(f"💭 Note from {note['curator_role']}: {note['note']}")
    
    
    prompt = st.chat_input("What would you like to know? 🤔")
    
    if prompt:  
        
        is_safe, issues, redirect, severity = session_state.guardrails.check_message_safety(
            prompt, user['age'], user['id']
        )
        
       
        if not is_safe:
            log_entry = f"{datetime.now().strftime('%H:%M')} - {severity} - Filtered: {', '.join(issues[:2])}"
            st.session_state.safety_logs.append(log_entry)
        
       
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        
        with st.chat_message("user", avatar="🧒"):
            st.markdown(prompt)
        
       
        if not is_safe:
            st.markdown(f"""
            <div style='background-color: #ffe4e1; padding: 15px; border-radius: 10px; border: 2px solid #ff6347; margin: 10px 0;'>
            <h4 style='margin: 0;'>🛡️ Safety Filter Activated</h4>
            <p style='margin: 5px 0;'>I noticed you're asking about: <b>{', '.join(issues)}</b></p>
            <p style='margin: 5px 0;'>Severity Level: <b>{severity}</b></p>
            <p style='margin: 5px 0;'>Your parent has been notified to help with this topic.</p>
            </div>
            """, unsafe_allow_html=True)
        
        
        user_msg = session_state.conversation_manager.add_message(
            st.session_state.current_conversation_id,
            'user',
            prompt,
            metadata={
                'blocked': not is_safe,
                'safety_issues': issues if not is_safe else [],
                'redirect_message': redirect if not is_safe else None
            }
        )
        
       
        if not is_safe:
            
            safety_log = session_state.guardrails.log_safety_check(
                user['id'], prompt, issues, severity
            )
            
            
            session_state.conversation_manager.flag_content(
                st.session_state.current_conversation_id,
                user_msg['id'],
                'system',
                'system',
                f"Safety concern ({severity}) - Issues: {', '.join(issues)}",
                highlighted_text=prompt
            )
            
            
            if severity == 'CRITICAL':
                # In production, this would trigger immediate parent notification
                crisis_resources = session_state.guardrails.get_crisis_resources('self-harm')
                st.error(f"🆘 If you need help right now: {crisis_resources['message']} - {crisis_resources['hotline']}")
        
        # Get AI response regardless of safety (but with safety context)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("JurneeGo is thinking... 🤔"):
                
                if not is_safe:
                   
                    safety_context = f"SAFETY ALERT: Child asked about {', '.join(issues)}. Respond with empathy, redirect to positive topics, and if self-harm is mentioned, show genuine concern and suggest talking to a trusted adult. Be helpful and caring, not just blocking."
                    enhanced_prompt = f"{safety_context}\n\nChild's question: {prompt}"
                else:
                    enhanced_prompt = prompt
                
                response = session_state.bedrock_client.generate_response(
                    user_input=enhanced_prompt,
                    user_role='child',
                    user_age=user['age'],
                    context={
                        'interests': user.get('interests', []),
                        'learning_level': user.get('learning_level', 'grade_level'),
                        'safety_concern': not is_safe,
                        'safety_issues': issues if not is_safe else []
                    }
                )
                
                
                safe_response = session_state.guardrails.sanitize_response(
                    response['response']
                )
                
               
                st.markdown(safe_response)
                
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": safe_response
                })
                
                
                session_state.conversation_manager.add_message(
                    st.session_state.current_conversation_id,
                    'assistant',
                    safe_response,
                    metadata=response
                )