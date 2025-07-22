'use client';
import { useState } from "react";
import Image from "next/image";
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import './App.css'
import ChatMessage from './components/ChatMessage'



export default function Home() {
  const handleSendButton = (inputText) => {
    setMessages([
      ...messages,
      {
        id: 1,
        type: "user",
        content: inputText,
        timestamp: new Date()
      }
    ])
  } 
  const [messages, setMessages] = useState([

  ])
  return (

    <div className="app">
      <div className="chat-container">
        <Header />
        
        <div className="messages-container">
          <div className="messages-wrapper">
            <div className="welcome-message">
            </div>
            <div>
              {messages.map((message,index) =>
                (
                  <ChatMessage key = {index} message={message}/>
                )
              )}
            </div>
          </div>
        </div>

        <ChatInput onSendClick={handleSendButton} ></ChatInput>
      </div>
    </div>

  );
}
