from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class ConversationManager:
    """Manage conversations with parent monitoring capabilities"""
    
    def __init__(self):
        # In production, this would use DB of choice
        # For prototype, we use in-memory storage
        self.conversations = {}
        self.parent_child_mapping = {}
        self.flagged_content = []
        
    def create_conversation(self, user_id: str, user_role: str, parent_id: Optional[str] = None) -> str:
        """Create a new conversation"""
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        
        self.conversations[conversation_id] = {
            'id': conversation_id,
            'user_id': user_id,
            'user_role': user_role,
            'parent_id': parent_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'bookmarks': [],
            'flags': []
        }
        
        # Map child to parent for monitoring
        if user_role == 'child' and parent_id:
            self.parent_child_mapping[user_id] = parent_id
        
        return conversation_id
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Add a message to conversation"""
        
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = {
            'id': f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'reactions': [],
            'curator_notes': []
        }
        
        self.conversations[conversation_id]['messages'].append(message)
        
        # Notify parent if child message (in production, this would be real-time)
        conv = self.conversations[conversation_id]
        if conv['user_role'] == 'child' and conv['parent_id']:
            self._notify_parent(conv['parent_id'], conversation_id, message)
        
        return message
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_child_conversations(self, parent_id: str) -> List[Dict]:
        """Get all conversations for children of a parent"""
        child_convs = []
        
        for conv_id, conv in self.conversations.items():
            if conv.get('parent_id') == parent_id:
                child_convs.append(conv)
        
        return child_convs
    
    def add_parent_reaction(
        self, 
        conversation_id: str, 
        message_id: str, 
        parent_id: str,
        reaction: str
    ) -> bool:
        """Add parent reaction to a message"""
        
        if conversation_id not in self.conversations:
            return False
        
        conv = self.conversations[conversation_id]
        
        # Verify parent has access
        if conv.get('parent_id') != parent_id:
            return False
        
        # Find and update message
        for msg in conv['messages']:
            if msg['id'] == message_id:
                msg['reactions'].append({
                    'user_id': parent_id,
                    'reaction': reaction,
                    'timestamp': datetime.now().isoformat()
                })
                return True
        
        return False
    
    def add_curator_note(
        self,
        conversation_id: str,
        message_id: str,
        curator_id: str,
        curator_role: str,
        note: str,
        highlighted_text: Optional[str] = None
    ) -> bool:
        """Add curator note to a message"""
        
        if conversation_id not in self.conversations:
            return False
        
        conv = self.conversations[conversation_id]
        
        # Verify curator has access
        if curator_role == 'parent' and conv.get('parent_id') != curator_id:
            return False
        # Add teacher verification logic here
        
        # Find and update message
        for msg in conv['messages']:
            if msg['id'] == message_id:
                msg['curator_notes'].append({
                    'curator_id': curator_id,
                    'curator_role': curator_role,
                    'note': note,
                    'highlighted_text': highlighted_text,
                    'timestamp': datetime.now().isoformat()
                })
                return True
        
        return False
    
    def bookmark_message(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str,
        bookmark_name: str,
        note: Optional[str] = None
    ) -> bool:
        """Bookmark a message"""
        
        if conversation_id not in self.conversations:
            return False
        
        bookmark = {
            'message_id': message_id,
            'user_id': user_id,
            'name': bookmark_name,
            'note': note,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversations[conversation_id]['bookmarks'].append(bookmark)
        return True
    
    def flag_content(
        self,
        conversation_id: str,
        message_id: str,
        flagger_id: str,
        flagger_role: str,
        reason: str,
        highlighted_text: Optional[str] = None
    ) -> bool:
        """Flag content for review"""
        
        flag = {
            'conversation_id': conversation_id,
            'message_id': message_id,
            'flagger_id': flagger_id,
            'flagger_role': flagger_role,
            'reason': reason,
            'highlighted_text': highlighted_text,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review'
        }
        
        self.flagged_content.append(flag)
        
        if conversation_id in self.conversations:
            self.conversations[conversation_id]['flags'].append(flag)
        
        return True
    
    def _notify_parent(self, parent_id: str, conversation_id: str, message: Dict):
        """Notify parent of new child message (placeholder for real-time notification)"""
        # In production, this would send real-time notification
        # For prototype, we'll just log it
        print(f"Parent notification: New message in child conversation {conversation_id}")
    
    def export_conversation(self, conversation_id: str) -> Optional[str]:
        """Export conversation as JSON"""
        if conversation_id in self.conversations:
            return json.dumps(self.conversations[conversation_id], indent=2)
        return None