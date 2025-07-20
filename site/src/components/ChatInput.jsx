import { motion } from 'framer-motion'
import { FileUpIcon, Send } from 'lucide-react'

const ChatInput = () => {
  return (
    <div 
      className="chat-input-container"
    >
      <div className="chat-input-form">
        <div className="input-wrapper">
          <input
            type="text"
            placeholder="Ask me anything about SSN..."
            className="message-input"
          />
          <button className="send-button">
            <Send size={20} />
          </button>
          <button className="file-button">
            <FileUpIcon size = {20}/>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInput
