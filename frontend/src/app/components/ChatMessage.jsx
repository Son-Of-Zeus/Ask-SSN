import { motion } from 'framer-motion'
import { Bot, User } from 'lucide-react'
import Citations from './Citations'
const ChatMessage = ({ message }) => {
  const isBot = message.type === 'assistant'
  
  return (
    <div
      className={`message ${isBot ? 'assistant-message' : 'user-message'}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="message-avatar">
        {isBot ? (
          <Bot size={20} className="avatar-icon" />
        ) : (
          <User size={20} className="avatar-icon" />
        )}
      </div>
      <div className="message-content">
        <div className="message-text">
          {message.content}
        </div>
        {isBot && <Citations citations={message.citations}></Citations>}
        <div className="message-time">
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
