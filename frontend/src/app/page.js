'use client';
import { useRef } from "react";
import { useEffect, useState } from "react";
import Image from "next/image";
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import './App.css'
import ChatMessage from './components/ChatMessage'



export default function Home() {
    const [messages, setMessages] = useState([

  ])

  const messagesEndRef = useRef(null);

  const scrollToBottom = () =>
  {
    messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


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

    fetch('/api/chat', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // body: JSON.stringify({ message: inputText }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      // You might want to update the chat UI with the response here

      setMessages([
      ...messages,
      {
        id: 1,
        type: "bot",
        content: data.content,
        timestamp: new Date()
      }
    ])
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }

  // const handleBotResponse = (inputText) => {
  //     setMessages([
  //     ...messages,
  //     {
  //       id: 1,
  //       type: "bot",
  //       content: inputText,
  //       timestamp: new Date()
  //     }
  //   ])
  // }

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
              <div ref ={messagesEndRef}/>
            </div>
          </div>
        </div>

        <ChatInput onSendClick={handleSendButton}></ChatInput>
      </div>
    </div>

  );
}
