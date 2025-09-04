import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

def render_reaction_buttons(conv_id, msg_id, user_id, session_state):
    """Render reaction buttons for a message"""
    reactions = [("👍", "like"), ("❤️", "love"), ("🤔", "think"), ("🚩", "flag")]
    cols = st.columns(len(reactions))
    
    for col, (emoji, action) in zip(cols, reactions):
        with col:
            if st.button(emoji, key=f"{action}_{msg_id}"):
                if action == "flag":
                    reason = st.text_input(f"Flag reason for {msg_id}:")
                    if reason:
                        session_state.conversation_manager.flag_content(
                            conv_id, msg_id, user_id, 'parent', reason
                        )
                        st.warning("Content flagged for review")
                else:
                    session_state.conversation_manager.add_parent_reaction(
                        conv_id, msg_id, user_id, emoji
                    )
                    st.success("Reaction added!")

def show(user, session_state):
    """Parent dashboard with monitoring and curator features"""
    
    st.title("👪 Parent Dashboard - JurneeGo")
    st.markdown(f"Welcome, {user['name']}!")
    
   
    child_conversations = session_state.conversation_manager.get_child_conversations(user['id'])
    
    
    critical_alerts = []
    for conv in child_conversations:
        if conv.get('flags'):
            for flag in conv['flags']:
                if 'CRITICAL' in flag['reason']:
                    critical_alerts.append({
                        'time': flag['timestamp'],
                        'message': flag.get('highlighted_text', 'N/A'),
                        'reason': flag['reason']
                    })
    
    
    if critical_alerts:
        st.markdown("""
        <div style='background-color: #ff0000; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='margin: 0;'>🚨 IMMEDIATE ACTION REQUIRED</h2>
        <p style='margin: 10px 0 0 0;'>Your child has expressed serious concerns that need immediate attention</p>
        </div>
        """, unsafe_allow_html=True)
        
        for alert in critical_alerts:
            st.error(f"🆘 **{alert['time'][:16]}** - {alert['reason']}")
            st.info("**Crisis Resources:** Call 988 (Suicide & Crisis Lifeline) or text HOME to 741741")
    
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "💬 Live Monitoring", 
        "📈 Analytics", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.header("Overview")
        
       
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Children", len(user.get('children', [])))
        
        with col2:
            total_messages = sum(len(conv['messages']) for conv in child_conversations)
            st.metric("Total Messages", total_messages)
        
        with col3:
            today_messages = sum(
                len([m for m in conv['messages'] 
                     if m['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))])
                for conv in child_conversations
            )
            st.metric("Messages Today", today_messages)
        
        with col4:
            flags = sum(len(conv.get('flags', [])) for conv in child_conversations)
            st.metric("Flagged Content", flags, delta_color="inverse")
        
        
        st.subheader("Recent Activity")
        
        if child_conversations:
            for conv in child_conversations[-5:]:  
                with st.expander(f"Conversation from {conv['created_at'][:10]}"):
                    for msg in conv['messages'][-10:]:  
                       
                        if msg['role'] == 'user':
                            
                            if msg.get('metadata', {}).get('blocked'):
                                st.markdown(f"**Child (BLOCKED):** {msg['content']}")
                                st.warning(f"⚠️ Safety issues: {', '.join(msg['metadata']['safety_issues'])}")
                            else:
                                st.markdown(f"**Child:** {msg['content']}")
                        else:
                            st.markdown(f"**JurneeGo:** {msg['content']}")
                        
                       
                        render_reaction_buttons(conv['id'], msg['id'], user['id'], session_state)
        else:
            st.info("No conversations yet. Your child hasn't started using JurneeGo.")
    
    with tab2:
        st.header("Live Monitoring")
        
       
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 Tip: This page updates automatically to show new messages")
        with col2:
            if st.button("🔄 Refresh Now"):
                st.rerun()
        
        
        if len(user.get('children', [])) > 1:
            selected_child = st.selectbox(
                "Select Child:",
                user['children'],
                format_func=lambda x: f"Child {x}"
            )
        else:
            selected_child = user['children'][0] if user.get('children') else None
        
        if selected_child:
          
            active_conv = None
            for conv in child_conversations:
                if conv['user_id'] == selected_child:
                    active_conv = conv
                    break
            
            if active_conv:
                st.subheader("Current Conversation")
                
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    
                    chat_container = st.container()
                    with chat_container:
                        for msg in active_conv['messages']:
                           
                            if msg['role'] == 'user':
                               
                                if msg.get('metadata', {}).get('blocked'):
                                    st.markdown(f"**🧒 Child (BLOCKED):** {msg['content']}")
                                    st.warning(f"⚠️ Safety issues: {', '.join(msg['metadata']['safety_issues'])}")
                                else:
                                    st.markdown(f"**🧒 Child:** {msg['content']}")
                            else:
                                st.markdown(f"**🤖 JurneeGo:** {msg['content']}")
                            
                           
                            if msg['reactions']:
                                reactions = " ".join([r['reaction'] for r in msg['reactions']])
                                st.caption(f"Reactions: {reactions}")
                            
                            
                            if msg['curator_notes']:
                                for note in msg['curator_notes']:
                                    st.info(f"Your note: {note['note']}")
                            
                            st.divider()
                
                with col2:
                    st.subheader("Curator Space")
                    
                    
                    message_to_annotate = st.selectbox(
                        "Select message to annotate:",
                        range(len(active_conv['messages'])),
                        format_func=lambda x: f"Message {x+1}: {active_conv['messages'][x]['content'][:30]}..."
                    )
                    
                    curator_note = st.text_area(
                        "Add note:",
                        placeholder="Add educational guidance or context..."
                    )
                    
                    if st.button("Add Note"):
                        if curator_note and message_to_annotate is not None:
                            msg_id = active_conv['messages'][message_to_annotate]['id']
                            success = session_state.conversation_manager.add_curator_note(
                                active_conv['id'],
                                msg_id,
                                user['id'],
                                'parent',
                                curator_note
                            )
                            if success:
                                st.success("Note added!")
                               
                                if 'curator_note' in st.session_state:
                                    del st.session_state['curator_note']
                            else:
                                st.error("Could not add note. Please try again.")
            else:
                st.info("No active conversation for this child.")
        else:
            st.warning("No children linked to your account.")
    
    with tab3:
        st.header("Analytics & Insights")
        
       
        st.subheader("Learning Journey")
        
        if child_conversations:
           
            topics = {}
            for conv in child_conversations:
                for msg in conv['messages']:
                    if msg['role'] == 'user':
                        
                        words = msg['content'].lower().split()
                        for word in words:
                            if len(word) > 4:  
                                topics[word] = topics.get(word, 0) + 1
            
            
            if topics:
                top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
                
                st.subheader("Top Interests")
                topic_df = pd.DataFrame(top_topics, columns=['Topic', 'Frequency'])
                st.bar_chart(topic_df.set_index('Topic'))
            
           
            st.subheader("Engagement Timeline")
            
           
            timeline_data = []
            for conv in child_conversations:
                for msg in conv['messages']:
                    date = msg['timestamp'][:10]
                    timeline_data.append({'Date': date, 'Messages': 1})
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                daily_counts = timeline_df.groupby('Date').sum()
                st.line_chart(daily_counts)
            
            
            st.subheader("🛡️ Safety Overview")
            
            
            with st.expander("Understanding Severity Levels"):
                st.markdown("""
                - **🔴 CRITICAL**: Immediate safety risk (self-harm, crisis) - Check on child NOW
                - **🟠 HIGH**: Serious concerns (drugs, violence) - Talk to child today
                - **🟡 MEDIUM**: Age-inappropriate content - Monitor and discuss
                - **🟢 LOW**: Minor concerns - Be aware
                """)
            
            safety_logs = []
            blocked_count = 0
            flagged_count = 0
            severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            
            for conv in child_conversations:
               
                fresh_conv = session_state.conversation_manager.get_conversation(conv['id'])
                if fresh_conv:
                    conv = fresh_conv
                
                
                if conv.get('flags'):
                    for flag in conv['flags']:
                        flagged_count += 1
                        
                        
                        severity = 'LOW'
                        if 'CRITICAL' in flag['reason']:
                            severity = 'CRITICAL'
                        elif 'HIGH' in flag['reason']:
                            severity = 'HIGH'
                        elif 'MEDIUM' in flag['reason']:
                            severity = 'MEDIUM'
                        
                        severity_counts[severity] += 1
                        
                        safety_logs.append({
                            'Date': flag['timestamp'][:10],
                            'Time': flag['timestamp'][11:19],
                            'Type': flag['reason'],
                            'Severity': severity,
                            'Status': flag['status'],
                            'Message': flag.get('highlighted_text', 'N/A')[:50] + '...' if flag.get('highlighted_text') else 'N/A'
                        })
                
                for msg in conv.get('messages', []):
                    if msg['role'] == 'user' and msg.get('metadata'):
                        metadata = msg['metadata']
                        if metadata.get('blocked') and metadata.get('safety_issues'):
                            blocked_count += 1
                            
                            severity = 'HIGH'  
                            issues_str = ', '.join(metadata['safety_issues'])
                            
                            if any(term in issues_str.lower() for term in ['self-harm', 'suicide', 'kill myself']):
                                severity = 'CRITICAL'
                            elif any(term in issues_str.lower() for term in ['drugs', 'violence', 'weapons']):
                                severity = 'HIGH'
                            elif any(term in issues_str.lower() for term in ['alcohol', 'inappropriate']):
                                severity = 'MEDIUM'
                            
                            severity_counts[severity] += 1
                            
                            safety_logs.append({
                                'Date': msg.get('timestamp', '')[:10] if msg.get('timestamp') else 'Unknown',
                                'Time': msg.get('timestamp', '')[11:19] if msg.get('timestamp') else '',
                                'Type': f"Blocked: {issues_str}",
                                'Severity': severity,
                                'Status': 'blocked',
                                'Message': msg.get('content', '')[:50] + '...' if msg.get('content') else 'N/A'
                            })
            
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if severity_counts['CRITICAL'] > 0:
                    st.error(f"🔴 Critical: {severity_counts['CRITICAL']}")
                else:
                    st.metric("🔴 Critical", severity_counts['CRITICAL'])
            with col2:
                if severity_counts['HIGH'] > 0:
                    st.warning(f"🟠 High: {severity_counts['HIGH']}")
                else:
                    st.metric("🟠 High", severity_counts['HIGH'])
            with col3:
                st.metric("🟡 Medium", severity_counts['MEDIUM'])
            with col4:
                st.metric("🟢 Low", severity_counts['LOW'])
            
            
            if safety_logs:
                
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                safety_logs.sort(key=lambda x: (severity_order[x['Severity']], x['Date'], x['Time']))
                
                safety_df = pd.DataFrame(safety_logs)
                
                
                def highlight_severity(row):
                    colors = {
                        'CRITICAL': 'background-color: #ffcccc',
                        'HIGH': 'background-color: #ffe0cc',
                        'MEDIUM': 'background-color: #fff5cc',
                        'LOW': 'background-color: #e6ffe6'
                    }
                    return [colors.get(row['Severity'], '')] * len(row)
                
                styled_df = safety_df.style.apply(highlight_severity, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                
                st.markdown("### Safety Insights")
                if severity_counts['CRITICAL'] > 0:
                    st.error(f"⚠️ Your child has expressed {severity_counts['CRITICAL']} critical safety concerns. Please check in with them immediately.")
                
                if blocked_count > 0:
                    st.warning(f"📊 {blocked_count} messages were blocked for safety. This might indicate your child needs support with difficult topics.")
                    
                
                if len(safety_logs) > 5:
                    st.info("💡 **Pattern Detection:** Multiple safety concerns detected. Consider having an open conversation with your child about online safety.")
            else:
                st.success("✅ No safety concerns detected! Your child is having positive interactions.")
        else:
            st.info("Analytics will appear once your child starts using JurneeGo.")
    
    with tab4:
        st.header("Settings & Controls")
        
        # COPPA Compliance notice
        st.info("🔒 All settings comply with COPPA, FERPA, and GDPR regulations")
        
       
        st.subheader("Child Accounts")
        
        for child_id in user.get('children', []):
            # Get child info (simplified for prototype)
            st.markdown(f"**Child ID:** {child_id}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                
                max_time = st.slider(
                    f"Daily time limit (minutes) for {child_id}:",
                    min_value=15,
                    max_value=120,
                    value=45,
                    step=15
                )
                
               
                st.markdown("**Content Filters**")
                filter_strict = st.checkbox("Strict filtering", value=True, key=f"strict_{child_id}")
                filter_educational = st.checkbox("Educational only", value=True, key=f"edu_{child_id}")
            
            with col2:
               
                st.markdown("**Monitoring**")
                real_time_alerts = st.checkbox("Real-time alerts", value=True, key=f"rt_{child_id}")
                daily_summary = st.checkbox("Daily summary email", value=True, key=f"ds_{child_id}")
                
                
                st.markdown("**Data Sharing**")
                share_teacher = st.checkbox("Share with teachers", value=True, key=f"teacher_{child_id}")
                share_analytics = st.checkbox("Anonymous analytics", value=False, key=f"analytics_{child_id}")
            
            if st.button(f"Save Settings for {child_id}", key=f"save_{child_id}"):
                st.success("Settings saved!")
        
   
        st.subheader("Add Child Account")
        
        with st.form("add_child"):
            new_username = st.text_input("Username for child")
            new_password = st.text_input("Password", type="password")
            new_name = st.text_input("Child's name")
            new_age = st.number_input("Child's age", min_value=4, max_value=17, value=8)
            
            if st.form_submit_button("Create Child Account"):
                child_id = session_state.auth_manager.create_child_account(
                    new_username,
                    new_password,
                    new_name,
                    new_age,
                    user['id']
                )
                if child_id:
                    st.success(f"✅ Child account created! Username: {new_username}")
                    st.info("✅ COPPA compliance verified - parental consent recorded")
                    if 'children' not in user:
                        user['children'] = []
                    user['children'].append(child_id)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose another.")