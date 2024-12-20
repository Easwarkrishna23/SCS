from database import Message, User
from crypto_utils import CryptoManager
from datetime import datetime
from typing import List, Dict
import json

class MessageHandler:
    def __init__(self, db_session, graph_manager):
        self.db_session = db_session
        self.graph_manager = graph_manager
        self.crypto_manager = CryptoManager()

    def send_message(self, sender_id: int, receiver_id: int, message: str) -> bool:
        """Send an encrypted message from sender to receiver"""
        try:
            # Get the shortest path
            path = self.graph_manager.get_shortest_path(sender_id, receiver_id)
            if not path:
                return False, "No valid path found between sender and receiver"

            # Get receiver's key
            receiver = self.db_session.query(User).filter_by(node_id=receiver_id).first()
            if not receiver:
                return False, "Receiver not found"

            # Encrypt message
            encrypted_content = self.crypto_manager.encrypt_message(message, receiver.password.encode())

            # Create message record
            new_message = Message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                encrypted_content=encrypted_content,
                sent_at=datetime.utcnow(),
                read=False
            )

            self.db_session.add(new_message)
            self.db_session.commit()

            return True, "Message sent successfully"

        except Exception as e:
            return False, f"Error sending message: {str(e)}"

    def get_unread_messages(self, user_id: int) -> List[Dict]:
        """Get all unread messages for a user"""
        unread_messages = self.db_session.query(Message).filter_by(
            receiver_id=user_id,
            read=False
        ).all()

        messages_list = []
        for msg in unread_messages:
            sender = self.db_session.query(User).filter_by(id=msg.sender_id).first()
            messages_list.append({
                'id': msg.id,
                'sender_username': sender.username,
                'encrypted_content': msg.encrypted_content,
                'sent_at': msg.sent_at.isoformat(),
                'read': msg.read
            })

        return messages_list

    def get_conversation_history(self, user1_id: int, user2_id: int) -> List[Dict]:
        """Get conversation history between two users"""
        messages = self.db_session.query(Message).filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.sent_at).all()

        history = []
        for msg in messages:
            sender = self.db_session.query(User).filter_by(id=msg.sender_id).first()
            receiver = self.db_session.query(User).filter_by(id=msg.receiver_id).first()
            
            history.append({
                'id': msg.id,
                'sender_username': sender.username,
                'receiver_username': receiver.username,
                'encrypted_content': msg.encrypted_content,
                'sent_at': msg.sent_at.isoformat(),
                'read': msg.read
            })

        return history

    def mark_as_read(self, message_id: int) -> bool:
        """Mark a message as read"""
        message = self.db_session.query(Message).filter_by(id=message_id).first()
        if message:
            message.read = True
            self.db_session.commit()
            return True
        return False

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (only if user is sender or receiver)"""
        message = self.db_session.query(Message).filter_by(id=message_id).first()
        if message and (message.sender_id == user_id or message.receiver_id == user_id):
            self.db_session.delete(message)
            self.db_session.commit()
            return True
        return False

    def get_user_messages_summary(self, user_id: int) -> Dict:
        """Get summary of user's messages"""
        total_sent = self.db_session.query(Message).filter_by(sender_id=user_id).count()
        total_received = self.db_session.query(Message).filter_by(receiver_id=user_id).count()
        unread_count = self.db_session.query(Message).filter_by(
            receiver_id=user_id,
            read=False
        ).count()

        return {
            'total_sent': total_sent,
            'total_received': total_received,
            'unread_count': unread_count
        }