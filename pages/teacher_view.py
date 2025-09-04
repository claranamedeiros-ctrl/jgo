import streamlit as st
import pandas as pd
from datetime import datetime

def show(user, session_state):
    """Teacher view with class management and curriculum tools"""
    
    st.title("🎓 Teacher Dashboard - JurneeGo")
    st.markdown(f"Welcome, {user['name']}!")
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Class Overview",
        "👥 Student Activity",
        "📝 Learning Design",
        "📊 Analytics",
        "💬 Group Spaces"
    ])
    
    with tab1:
        st.header("Class Overview")
        
        # Class selection (for prototype, using demo data)
        selected_class = st.selectbox(
            "Select Class:",
            user.get('classes', ['class_001']),
            format_func=lambda x: f"Class {x[-3:]}"
        )
        
        # Class stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Students", "24")  # Demo data
        
        with col2:
            st.metric("Questions Today", "156")
        
        with col3:
            st.metric("Learning Goals Met", "18/20")
        
        with col4:
            st.metric("Parent Engagement", "85%")
        
        # Recent class activity
        st.subheader("Recent Class Activity")
        
        # Demo activity data
        activities = [
            {"student": "Alex M.", "question": "Why do plants need sunlight?", "time": "10 mins ago", "topic": "Science"},
            {"student": "Sarah L.", "question": "How do I solve 45 + 67?", "time": "15 mins ago", "topic": "Math"},
            {"student": "James K.", "question": "What makes volcanoes erupt?", "time": "22 mins ago", "topic": "Science"},
            {"student": "Emma R.", "question": "Can you help me with spelling 'necessary'?", "time": "30 mins ago", "topic": "Language"},
        ]
        
        for activity in activities:
            with st.expander(f"{activity['student']} - {activity['topic']} ({activity['time']})"):
                st.markdown(f"**Question:** {activity['question']}")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("⭐ Promote", key=f"promote_{activity['student']}"):
                        st.success("Question promoted to class!")
                with col_b:
                    if st.button("💬 Comment", key=f"comment_{activity['student']}"):
                        st.text_input("Add comment:", key=f"comment_input_{activity['student']}")
                with col_c:
                    if st.button("✅ Verify Learning", key=f"verify_{activity['student']}"):
                        st.success("Learning goal verified!")
    
    with tab2:
        st.header("Student Activity Monitor")
        
        # Student list with activity indicators
        students = [
            {"name": "Alex M.", "status": "🟢 Active", "questions": 12, "time": "25 min", "progress": 85},
            {"name": "Sarah L.", "status": "🟢 Active", "questions": 8, "time": "18 min", "progress": 72},
            {"name": "James K.", "status": "🟡 Away", "questions": 15, "time": "30 min", "progress": 90},
            {"name": "Emma R.", "status": "🔴 Offline", "questions": 6, "time": "12 min", "progress": 65},
        ]
        
        # Display as table
        student_df = pd.DataFrame(students)
        st.dataframe(
            student_df,
            column_config={
                "progress": st.column_config.ProgressColumn(
                    "Learning Progress",
                    help="Progress towards daily learning goals",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Individual student view
        selected_student = st.selectbox("View student details:", [s["name"] for s in students])
        
        if selected_student:
            st.subheader(f"Detailed View: {selected_student}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Recent questions
                st.markdown("**Recent Questions:**")
                sample_questions = [
                    "What is photosynthesis?",
                    "How do fractions work?",
                    "Why is the sky blue?",
                    "What happened in the American Revolution?"
                ]
                
                for q in sample_questions[:3]:
                    with st.container():
                        st.markdown(f"❓ {q}")
                        if st.button(f"View conversation", key=f"view_{q[:10]}"):
                            st.info("Opening conversation view...")
            
            with col2:
                # Learning metrics
                st.markdown("**Learning Metrics:**")
                st.metric("Questions Asked", "45")
                st.metric("Topics Explored", "12")
                st.metric("Parent Engagement", "High")
                
                # Quick actions
                st.markdown("**Quick Actions:**")
                if st.button("📧 Message Parent"):
                    st.info("Opening parent communication...")
                if st.button("📋 Assign Task"):
                    st.info("Opening task assignment...")
    
    with tab3:
        st.header("Learning Journey Design")
        
        # Create learning goals
        st.subheader("Set Learning Goals")
        
        with st.form("learning_goals"):
            goal_title = st.text_input("Learning Goal Title")
            
            # Standards alignment
            standards = st.multiselect(
                "Aligned Standards:",
                ["CCSS.MATH.4.OA.1", "CCSS.ELA.4.RI.1", "NGSS.4-PS3-1", "NCSS.4.1"]
            )
            
            goal_description = st.text_area(
                "Goal Description:",
                placeholder="Describe what students should learn..."
            )
            
            # Assessment criteria
            st.markdown("**Success Criteria:**")
            criteria1 = st.text_input("Criterion 1")
            criteria2 = st.text_input("Criterion 2")
            criteria3 = st.text_input("Criterion 3")
            
            if st.form_submit_button("Create Learning Goal"):
                st.success(f"Learning goal '{goal_title}' created!")
        
        # Upload materials
        st.subheader("Upload Learning Materials")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt'],
            help="Upload reading materials or assignments"
        )
        
        if uploaded_file:
            material_type = st.radio(
                "Material Type:",
                ["Reading Material", "Individual Assignment", "Group Assignment"]
            )
            
            if st.button("Upload to JurneeGo"):
                if uploaded_file and material_type:
                    st.success(f"{material_type} uploaded successfully!")
                    # In production, would save to S3 or database
                else:
                    st.warning("Please select a file and material type first")
        
        # AI lesson planning
        st.subheader("AI Lesson Planning Assistant")
        
        lesson_topic = st.text_input("Lesson Topic:")
        grade_level = st.selectbox("Grade Level:", ["3rd", "4th", "5th", "6th"])
        duration = st.select_slider("Duration:", ["30 min", "45 min", "60 min", "90 min"])
        
        if st.button("Generate Lesson Plan"):
            if lesson_topic:
                with st.spinner("Generating lesson plan..."):
                    # In production, this would call the AI
                    st.markdown("### Generated Lesson Plan")
                    st.markdown(f"**Topic:** {lesson_topic}")
                    st.markdown(f"**Grade:** {grade_level}")
                    st.markdown(f"**Duration:** {duration}")
                    st.markdown("""
                    **Objectives:**
                    1. Students will understand key concepts
                    2. Students will apply knowledge through practice
                    3. Students will demonstrate learning through discussion
                    
                    **Activities:**
                    - Opening: Interactive question session (10 min)
                    - Main: Guided exploration with JurneeGo (20 min)
                    - Practice: Individual/group exercises (15 min)
                    - Closing: Reflection and sharing (10 min)
                    """)
    
    with tab4:
        st.header("Class Analytics")
        
        # Learning progress overview
        st.subheader("Class Learning Progress")
        
        # Sample data for visualization
        progress_data = pd.DataFrame({
            'Subject': ['Math', 'Science', 'Language', 'Social Studies'],
            'Class Average': [78, 85, 82, 75],
            'Goal': [80, 80, 80, 80]
        })
        
        st.bar_chart(progress_data.set_index('Subject'))
        
        # Standards mastery
        st.subheader("Standards Mastery")
        
        standards_data = [
            {"Standard": "CCSS.MATH.4.OA.1", "Mastery": 85, "Students": "20/24"},
            {"Standard": "CCSS.ELA.4.RI.1", "Mastery": 78, "Students": "18/24"},
            {"Standard": "NGSS.4-PS3-1", "Mastery": 72, "Students": "17/24"},
        ]
        
        standards_df = pd.DataFrame(standards_data)
        st.dataframe(
            standards_df,
            column_config={
                "Mastery": st.column_config.ProgressColumn(
                    "Mastery Level",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Engagement trends
        st.subheader("Weekly Engagement Trends")
        
        # Sample trend data
        dates = pd.date_range(start='2025-08-25', periods=7, freq='D')
        engagement_data = pd.DataFrame({
            'Date': dates,
            'Questions': [120, 145, 138, 165, 172, 155, 142],
            'Active Students': [22, 24, 23, 24, 24, 22, 20]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(engagement_data.set_index('Date')['Questions'])
        with col2:
            st.line_chart(engagement_data.set_index('Date')['Active Students'])
    
    with tab5:
        st.header("Group Spaces")
        
        # Create group
        st.subheader("Create New Group")
        
        with st.form("create_group"):
            group_name = st.text_input("Group Name")
            group_members = st.multiselect(
                "Select Members:",
                [s["name"] for s in students]
            )
            group_task = st.text_area("Group Task/Project")
            
            if st.form_submit_button("Create Group"):
                if group_name and group_members:
                    st.success(f"Group '{group_name}' created with {len(group_members)} members!")
        
        # Existing groups
        st.subheader("Active Groups")
        
        groups = [
            {"name": "Science Explorers", "members": 4, "status": "🟢 Active", "progress": 65},
            {"name": "Math Champions", "members": 3, "status": "🟢 Active", "progress": 80},
            {"name": "Reading Club", "members": 5, "status": "🟡 Paused", "progress": 45},
        ]
        
        for group in groups:
            with st.expander(f"{group['name']} ({group['members']} members) - {group['status']}"):
                st.progress(group['progress'] / 100)
                st.markdown(f"Progress: {group['progress']}%")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Enter as Curator", key=f"curator_{group['name']}"):
                        st.info("Entering group space as curator...")
                with col2:
                    if st.button("View Activity", key=f"activity_{group['name']}"):
                        st.info("Loading group activity...")
                with col3:
                    if st.button("Send Message", key=f"message_{group['name']}"):
                        st.text_input("Message to group:", key=f"msg_input_{group['name']}")