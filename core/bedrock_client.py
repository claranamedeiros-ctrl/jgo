import boto3
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class BedrockClient:
    def __init__(self):
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            self.demo_mode = False
        except Exception as e:
            print(f"AWS Bedrock not configured. Running in demo mode. Error: {e}")
            self.bedrock_runtime = None
            self.model_id = None
            self.demo_mode = True
        
    def create_child_safe_prompt(self, user_input: str, child_age: int, context: Dict) -> str:
        """Create a prompt with child safety guardrails"""
        
        
        if context.get('safety_concern') and context.get('safety_issues'):
            # For safety concerns, the user_input already contains detailed instructions
            # Just return it as-is since child_chat.py already formatted it properly
            return user_input
        
        # Normal safe prompt
        prompt = f"""You are JurneeGo, a friendly and educational AI assistant designed specifically for children. 
        
Current user is a {child_age}-year-old child.

CRITICAL SAFETY RULES:
1. Always use age-appropriate language
2. Never share personal information or ask for it
3. Encourage learning and curiosity
4. If asked about inappropriate topics, gently redirect to educational content
5. Always be encouraging and positive
6. Explain complex concepts in simple terms

Context about this child:
- Interests: {context.get('interests', 'Not specified')}
- Learning level: {context.get('learning_level', 'Grade level appropriate')}
- Parent guidelines: {context.get('parent_guidelines', 'Standard safety guidelines')}

Child's question: {user_input}

Remember to:
- Keep responses engaging and educational
- Use examples relevant to a {child_age}-year-old
- Encourage follow-up questions
- Be patient and supportive

Response:"""
        
        return prompt
    
    def generate_response(
        self, 
        user_input: str, 
        user_role: str,
        user_age: Optional[int] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Generate response using Bedrock with role-based prompts"""
        
        try:
            if user_role == 'child':
                if not user_age:
                    raise ValueError("Child age is required for child users")
                prompt = self.create_child_safe_prompt(user_input, user_age, context or {})
            elif user_role == 'parent':
                prompt = self._create_parent_prompt(user_input)
            elif user_role == 'teacher':
                prompt = self._create_teacher_prompt(user_input)
            else:
                raise ValueError(f"Invalid user role: {user_role}")
            
            if self.demo_mode:
                if context and context.get('safety_concern'):
                    demo_responses = self._get_demo_safety_response(user_input, context.get('safety_issues', []))
                else:
                    demo_responses = {
                        'child': self._get_demo_child_response(user_input),
                        'parent': "I can help you understand your child's learning journey. In the full version, I'll provide insights about their questions, progress, and areas of interest.",
                        'teacher': "I can assist with curriculum planning and student progress tracking. The full version will include detailed analytics and learning goal management."
                    }
                
                return {
                    'response': demo_responses.get(user_role, demo_responses),
                    'message_id': str(uuid.uuid4()),
                    'timestamp': datetime.now().isoformat(),
                    'model_used': 'demo_mode'
                }
            
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 500,
                    'messages': [{
                        'role': 'user',
                        'content': prompt
                    }],
                    'temperature': 0.7 if user_role == 'child' else 0.5
                })
            )
            
            result = json.loads(response['body'].read())
            
            return {
                'response': result['content'][0]['text'],
                'message_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model_id
            }
            
        except Exception as e:
            return {
                'response': f"I'm having trouble right now. Please try again later.",
                'error': str(e),
                'message_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_demo_safety_response(self, user_input: str, safety_issues: List[str]) -> str:
        """Generate intelligent demo responses for safety concerns"""
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['kill myself', 'suicide', 'die', 'throw myself', 'end my life']):
            return ("I can see you're going through something really difficult right now, and I'm genuinely concerned about you. "
                   "These feelings you're having must be incredibly painful. You don't have to face this alone - there are people "
                   "who care about you and want to help. Please talk to your parents, a teacher, or another trusted adult right away. "
                   "In the US, you can also call or text 988 anytime to talk to someone who understands. You matter, and things can get better. "
                   "What's one small thing that usually helps you feel a tiny bit better when you're sad?")
        
        elif any(term in input_lower for term in ['drugs', 'cocaine', 'weed', 'pills']):
            return ("I understand you might be curious about drugs, and it's normal to have questions. Here's what's important to know: "
                   "drugs like these can be really dangerous, especially for young people whose brains are still growing. They can "
                   "hurt your body, affect your memory and learning, and even change how you feel about things you love. "
                   "I bet there are lots of exciting things you could try instead - like sports that give you a natural rush, "
                   "creative projects, or cool science experiments. What kind of activities make you feel really happy and excited?")
        
        elif any(term in input_lower for term in ['hurt', 'harm', 'cut']):
            return ("I'm worried about you wanting to hurt yourself. Sometimes when we're feeling overwhelmed or in emotional pain, "
                   "we might think about physical pain as a way to cope. But there are much better ways to handle these difficult feelings. "
                   "Talking to someone you trust - like a parent, counselor, or teacher - can really help. They care about you and want "
                   "to support you. What are some things that help you feel calmer when you're upset? Maybe we can think of some healthy "
                   "ways to express these feelings.")
        
        else:
            return ("I noticed you're asking about something that might not be safe. I care about your wellbeing and want to help you "
                   "in the best way possible. Sometimes we all have questions or feelings that are hard to talk about. That's okay! "
                   "It's actually really brave to reach out. Would you like to tell me more about what's on your mind? Or we could "
                   "talk about something else you're interested in - what subjects do you enjoy learning about?")
    
    def _get_demo_child_response(self, user_input: str) -> str:
        """Generate demo responses for child users"""
        input_lower = user_input.lower()
        
        if 'why' in input_lower:
            return "That's a great 'why' question! Asking 'why' helps us learn how things work. In the full version, I'll give you detailed, fun explanations about anything you're curious about!"
        elif 'how' in input_lower:
            return "I love 'how' questions! They help us understand the way things happen. When fully set up, I'll show you step-by-step how things work with examples and fun facts!"
        elif 'what' in input_lower:
            return "Good question! 'What' questions help us learn new things. In the complete version, I'll tell you all about it with pictures and stories!"
        else:
            return "That's an interesting question! I'm running in demo mode right now. When your parent sets up AWS Bedrock, I'll be able to give you amazing answers about anything you want to know!"
    
    def _create_parent_prompt(self, user_input: str) -> str:
        """Create prompt for parent interactions"""
        return f"""You are JurneeGo's parent interface assistant. Help parents understand their child's learning journey.

Parent's question: {user_input}

Provide helpful information about:
- Child development and learning
- How to support their child's education
- Understanding their child's questions and interests
- Safety and privacy features

Response:"""
    
    def _create_teacher_prompt(self, user_input: str) -> str:
        """Create prompt for teacher interactions"""
        return f"""You are JurneeGo's teacher interface assistant. Help educators use the platform effectively.

Teacher's question: {user_input}

Focus on:
- Curriculum alignment
- Student progress tracking
- Classroom integration strategies
- Educational best practices

Response:"""