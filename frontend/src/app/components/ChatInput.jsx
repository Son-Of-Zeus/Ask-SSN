'use client';
import { useState } from 'react';
import { motion } from 'framer-motion'
import { FileUpIcon, Send } from 'lucide-react'


const ChatInput = ({onSendClick, updateChat}) => {
  const [inputText,setInputText] = useState('');

  const handleSend = ()=>
  {
    if (inputText.trim()) // I'm assuming this is to handle empty enters.
    {
      onSendClick(inputText);
      setInputText('');
    }
  }

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
            value={inputText}
            onChange={(e)=>setInputText(e.target.value)}
            onKeyPress={(e)=>e.key == 'Enter' && handleSend()}
          />
          <button className="send-button" onClick={handleSend}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInput
