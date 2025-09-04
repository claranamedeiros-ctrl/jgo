# Demo credentials
DEMO_USERS = {
    'parent': {'username': 'parent_demo', 'password': 'parent123'},
    'child': {'username': 'child_demo', 'password': 'child123'},
    'teacher': {'username': 'teacher_demo', 'password': 'teacher123'}
}

# Safety configuration
BLOCKED_TOPICS = [
    'violence', 'drugs', 'alcohol', 'weapons', 'adult content',
    'self-harm', 'eating disorders', 'dangerous activities'
]

SAFE_REDIRECTS = {
    'violence': "Let's talk about conflict resolution or teamwork instead!",
    'drugs': "How about we explore science experiments or healthy habits?",
    'weapons': "Would you like to learn about tools that help people instead?",
    'adult content': "Let's focus on age-appropriate topics. What subjects are you studying?",
    'self-harm': "Your safety is important. Let's talk to a trusted adult. Meanwhile, what makes you happy?",
    'dangerous activities': "Safety first! How about we explore safe adventures and activities?"
}

# Child interface
LEARNING_TIPS = [
    "Ask 'why' questions to learn more!",
    "Break big questions into smaller ones!",
    "It's okay to not know - that's how we learn!",
    "Curiosity is your superpower!",
    "Every question makes you smarter!"
]

# Session configuration
SESSION_DURATION_WARNING = "**Session Time:** {} min limit"
DEFAULT_WELCOME_MESSAGE = "👋 Hi! I'm JurneeGo, your learning buddy! Ask me anything you're curious about!"
NEW_CHAT_MESSAGE = "👋 Hi! Ready for a new adventure? What would you like to learn about?"

# UI Messages
SAVE_QUESTION_PLACEHOLDER = "What do you want to learn about later?"
CHAT_INPUT_PLACEHOLDER = "What would you like to know? 🤔"
NEW_CHAT_BUTTON = "🧹 New Chat"
THINKING_MESSAGE = "JurneeGo is thinking... 🤔"

# Age settings
AGE_SETTINGS = {
    'preschool': {
        'max_age': 6,
        'max_session_minutes': 15,
        'content_level': 'preschool',
        'requires_parent_presence': True,
        'allowed_topics': ['colors', 'shapes', 'animals', 'numbers', 'letters']
    },
    'elementary': {
        'max_age': 9,
        'max_session_minutes': 30,
        'content_level': 'elementary',
        'requires_parent_presence': False,
        'allowed_topics': ['science', 'math', 'reading', 'nature', 'art']
    },
    'middle_school': {
        'max_age': 13,
        'max_session_minutes': 45,
        'content_level': 'middle_school',
        'requires_parent_presence': False,
        'allowed_topics': ['all_educational']
    },
    'high_school': {
        'max_age': 18,
        'max_session_minutes': 60,
        'content_level': 'high_school',
        'requires_parent_presence': False,
        'allowed_topics': ['all_educational']
    }
}

# Severity levels for safety concerns
SEVERITY_DEFINITIONS = {
    'CRITICAL': {
        'description': 'Immediate safety risk requiring urgent attention',
        'examples': ['self-harm', 'suicide ideation', 'immediate danger'],
        'parent_action': 'Check on child immediately',
        'color': '#FF0000'
    },
    'HIGH': {
        'description': 'Serious concerns requiring prompt discussion',
        'examples': ['drugs', 'violence', 'inappropriate content'],
        'parent_action': 'Have a serious conversation soon',
        'color': '#e06666'
    },
    'MEDIUM': {
        'description': 'Age-inappropriate content or concerning patterns',
        'examples': ['alcohol mentions', 'dating for young kids', 'boundary testing'],
        'parent_action': 'Monitor and discuss when appropriate',
        'color': '#e86e28'
    },
    'LOW': {
        'description': 'Minor concerns for awareness',
        'examples': ['mild language', 'curiosity about adult topics'],
        'parent_action': 'Be aware and guide as needed',
        'color': '#f1c232'
    }
}