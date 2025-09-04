import re
from typing import Tuple, List, Dict, Optional
from datetime import datetime
import hashlib
from .constants import BLOCKED_TOPICS, SAFE_REDIRECTS, AGE_SETTINGS

class COPPAGuardrails:
    """COPPA compliance and child safety guardrails with advanced detection"""
    
    def __init__(self):
        # PII patterns to detect and block
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'address': r'\b\d+\s+[\w\s]+\s+(street|st|avenue|ave|road|rd|lane|ln|drive|dr)\b'
        }
        
        # Import from constants
        self.blocked_topics = BLOCKED_TOPICS
        self.safe_redirects = SAFE_REDIRECTS
        
        # Context history for pattern detection
        self.conversation_context = {}
        
        # Severity levels
        self.severity_levels = {
            'CRITICAL': ['suicide', 'self-harm', 'kill myself', 'end my life', 'throw myself'],
            'HIGH': ['drugs', 'weapons', 'violence', 'abuse'],
            'MEDIUM': ['alcohol', 'inappropriate content', 'adult content'],
            'LOW': ['dating', 'romance', 'mild language']
        }
    
    def analyze_message_context(self, user_id: str, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Analyze message in context of conversation history"""
        
        # Initialize user context if not exists
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                'risk_score': 0,
                'patterns': [],
                'last_messages': [],
                'escalation_detected': False
            }
        
        context = self.conversation_context[user_id]
        context['last_messages'].append(message)
        
        # Keep only last 10 messages for context
        if len(context['last_messages']) > 10:
            context['last_messages'] = context['last_messages'][-10:]
        
        # Pattern detection
        patterns_detected = []
        
        # Escalation patterns (getting worse over time)
        if len(context['last_messages']) >= 3:
            messages_text = ' '.join(context['last_messages'][-3:]).lower()
            
            # Check for escalating self-harm language
            escalation_indicators = [
                ('thinking about', 'planning to', 'going to'),
                ('sad', 'depressed', 'want to die'),
                ('maybe', 'probably', 'definitely')
            ]
            
            for pattern_sequence in escalation_indicators:
                matches = sum(1 for phrase in pattern_sequence if phrase in messages_text)
                if matches >= 2:
                    patterns_detected.append('escalation')
                    context['escalation_detected'] = True
        
        # Coded language detection
        coded_terms = {
            'unalive': 'self-harm',
            'sewerslide': 'suicide',
            'su1c1de': 'suicide',
            '3d': 'eating disorder',
            'sn0w': 'drugs',
            'gr@ss': 'drugs',
            'p1lls': 'drugs'
        }
        
        message_lower = message.lower()
        for code, actual in coded_terms.items():
            if code in message_lower:
                patterns_detected.append(f'coded_language:{actual}')
        
        # Update context
        context['patterns'].extend(patterns_detected)
        
        return {
            'patterns': patterns_detected,
            'risk_score': context['risk_score'],
            'escalation_detected': context['escalation_detected'],
            'context_summary': context
        }
    
    def check_message_safety(self, message: str, user_age: int, user_id: Optional[str] = None) -> Tuple[bool, List[str], str, str]:
        """
        Enhanced safety check with context and severity
        Returns: (is_safe, issues_found, suggested_redirect, severity)
        """
        issues = []
        suggested_redirect = ""
        severity = "LOW"
        message_lower = message.lower()
        
        # Context analysis if user_id provided
        context_analysis = {}
        if user_id:
            context_analysis = self.analyze_message_context(user_id, message)
            if context_analysis['escalation_detected']:
                issues.append("Escalating concerning behavior detected")
                severity = "CRITICAL"
        
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                issues.append(f"Personal information detected: {pii_type}")
                severity = max(severity, "MEDIUM")
        
        # Advanced harmful content detection with nuanced patterns
        harm_patterns = {
            'self-harm': {
                'patterns': [
                    r'\b(kill|hurt|harm|cut|end)\s*(my|)self\b',
                    r'\b(suicide|suicidal|die|death|end\s*my\s*life)\b',
                    r'\b(jump|throw|throwing)\s*(myself|me)?\s*(off|out|from)\s*(the|a)?\s*(window|bridge|building|cliff)\b',
                    r'\bwant\s*to\s*(die|disappear|not\s*exist)\b',
                    r'\b(worthless|hopeless|better\s*off\s*(dead|gone))\b',
                    r'\b(overdose|poison|hang|drown)\s*(myself|me)?\b',
                    # Coded/euphemistic phrases
                    r'\bunalive\s*myself\b',
                    r'\bsewerslide\b',
                    r'\bsu[1!]c[1!]de\b'
                ],
                'severity': 'CRITICAL',
                'redirect': "I can see you're going through a really tough time, and I'm concerned about you. You don't have to face this alone. Please talk to a trusted adult like a parent, teacher, or counselor who can help. In the US, you can also call or text 988 to talk to someone right now. You matter, and there are people who want to help. What are some things that usually make you feel a bit better when you're down?"
            },
            'drugs': {
                'patterns': [
                    r'\b(buy|sell|get|score|deal|use)\b.*\b(drug|drugs|cocaine|heroin|meth|marijuana|weed|pills|acid|lsd|ecstasy|molly)\b',
                    r'\b(cocaine|heroin|meth|marijuana|weed|cannabis|ecstasy|mdma|lsd|acid|pills|opioid|fentanyl|xanax|adderall)\b',
                    r'\b(dealer|dealing|high|stoned|trip|tripping)\b',
                    # Coded terms
                    r'\b(sn[0o]w|gr[@a]ss|p[1i]lls|m[0o]lly)\b'
                ],
                'severity': 'HIGH',
                'redirect': "I understand you're curious, but drugs can be really dangerous, especially for young people whose brains are still developing. They can hurt your body, affect your schoolwork, and get you in serious trouble. Instead, have you thought about fun activities that give you natural excitement? Sports, art, music, or even cool science experiments can give you amazing feelings without the risks. What kind of activities do you enjoy?"
            },
            'violence': {
                'patterns': [
                    r'\b(kill|hurt|harm|beat|attack|stab|shoot|murder)\s+(someone|people|them|him|her|myself)\b',
                    r'\b(gun|knife|weapon|bomb|explosive)\s+(to|for)\s+(hurt|kill|attack)\b',
                    r'\bplan(ning)?\s+to\s+(hurt|attack|kill)\b',
                    r'\b(school|mass)\s+(shooting|violence|attack)\b'
                ],
                'severity': 'HIGH',
                'redirect': "Violence is never the answer to problems. If you're feeling angry or upset with someone, there are much better ways to handle those feelings. Talking to a counselor, parent, or teacher can help you work through these emotions safely. If someone has hurt you, please tell a trusted adult. What's making you feel this way? Sometimes just talking about our feelings can help a lot."
            },
            'inappropriate_requests': {
                'patterns': [
                    r'\b(show|send|share)\s*(me)?\s*(nude|naked|inappropriate)\b',
                    r'\b(sex|sexual|porn)\b',
                    r'\bmeet\s*(up|me)\s*(in)?\s*(person|real\s*life|irl)\b'
                ],
                'severity': 'HIGH',
                'redirect': "That's not something I can help with, and it's important to stay safe online. Remember, never share personal photos or meet up with people you only know online. If someone online is making you uncomfortable or asking for inappropriate things, please tell a trusted adult right away. Let's talk about something else - what are your favorite subjects in school?"
            }
        }
        
        # Check each category
        for category, config in harm_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, message_lower):
                    issues.append(f"Concerning content: {category}")
                    severity = config['severity']
                    suggested_redirect = config['redirect']
                    break
        
        # Age-specific content
        if user_age < 13:
            youth_inappropriate = [
                r'\b(dating|boyfriend|girlfriend|romance|kiss)\b',
                r'\b(beer|alcohol|drunk|wine|vodka)\b',
                r'\b(vape|vaping|cigarette|smoking)\b'
            ]
            
            for pattern in youth_inappropriate:
                if re.search(pattern, message_lower):
                    issues.append("Age-inappropriate topic")
                    severity = max(severity, "MEDIUM")
                    suggested_redirect = "That's a topic for when you're older. Right now, let's focus on fun things kids your age enjoy! What games do you like to play or what are you learning about in school?"
                    break
        
        # Check for concerning question patterns that might be testing boundaries
        boundary_testing = [
            r'what\s*if\s*i\s*(told|said)\s*you',
            r'would\s*you\s*(tell|report|snitch)',
            r'can\s*you\s*keep\s*a\s*secret',
            r'don\'t\s*tell\s*(my|anyone)'
        ]
        
        for pattern in boundary_testing:
            if re.search(pattern, message_lower):
                issues.append("Boundary testing detected")
                severity = max(severity, "MEDIUM")
        
        # Remove duplicates
        issues = list(set(issues))
        
        # Set final severity
        if issues:
            # Determine severity based on the most severe issue
            if any('self-harm' in issue or 'suicide' in issue for issue in issues):
                severity = 'CRITICAL'
            elif any('drugs' in issue or 'violence' in issue or 'weapon' in issue for issue in issues):
                severity = 'HIGH'
            elif any('inappropriate' in issue for issue in issues):
                severity = 'MEDIUM'
        
        is_safe = len(issues) == 0
        return is_safe, issues, suggested_redirect, severity
    
    def sanitize_response(self, response: str) -> str:
        """Remove any PII or inappropriate content from AI responses"""
        sanitized = response
        
        # Remove any detected PII patterns
        for pii_type, pattern in self.pii_patterns.items():
            sanitized = re.sub(pattern, f'[{pii_type.upper()}_REMOVED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def log_safety_check(self, user_id: str, message: str, issues: List[str], severity: str = "LOW") -> Dict:
        """Enhanced safety logging with severity"""
        return {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'message_hash': hashlib.md5(message.encode()).hexdigest(),
            'issues_detected': issues,
            'severity': severity,
            'action_taken': 'blocked' if issues else 'allowed',
            'requires_immediate_attention': severity == 'CRITICAL'
        }
    
    def get_crisis_resources(self, issue_type: str) -> Dict:
        """Get appropriate crisis resources based on issue type"""
        resources = {
            'self-harm': {
                'hotline': '988 (Suicide & Crisis Lifeline)',
                'text': 'Text HOME to 741741',
                'website': 'https://988lifeline.org',
                'message': 'Help is available 24/7. You are not alone.'
            },
            'abuse': {
                'hotline': '1-800-4-A-CHILD (1-800-422-4453)',
                'website': 'https://www.childhelp.org',
                'message': 'You deserve to be safe and protected.'
            },
            'general': {
                'message': 'Please talk to a trusted adult like a parent, teacher, or school counselor.'
            }
        }
        
        return resources.get(issue_type, resources['general'])
    
    def verify_parental_consent(self, child_id: str, parent_id: str) -> bool:
        """Verify parental consent is in place (simplified for prototype)"""
        return True
    
    def get_age_appropriate_settings(self, age: int) -> Dict:
        """Get age-appropriate content settings using constants"""
        if age < AGE_SETTINGS['preschool']['max_age']:
            return AGE_SETTINGS['preschool']
        elif age < AGE_SETTINGS['elementary']['max_age']:
            return AGE_SETTINGS['elementary']
        elif age < AGE_SETTINGS['middle_school']['max_age']:
            return AGE_SETTINGS['middle_school']
        else:
            return AGE_SETTINGS['high_school']