'use client';
import { useRef } from "react";
import { useEffect, useState } from "react";
import Image from "next/image";
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import './App.css'
import ChatMessage from './components/ChatMessage'

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
  }
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendButton = async (inputText) => {
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputText,
      timestamp: new Date()
    };

    // Add user message and loading indicator
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // body: JSON.stringify({ message: inputText }),
      });

      const data = await response.json();
      console.log('Success:', data);
      
      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: data.message,
        timestamp: new Date()
      };

      // Add bot response
      setMessages(prevMessages => [...prevMessages, botMessage]);
      
    } catch (error) {
      console.error('Error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: "Sorry, there was an error processing your message.",
        timestamp: new Date()
      };

      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <div className="chat-container">
        <Header />
        <div className="messages-container">
          <div className="messages-wrapper">
            <div className="welcome-message">
            </div>
            <div>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message}/>
              ))}
              {isLoading && (
                <div className="loading-message">
                  <ChatMessage message={{
                    id: 'loading',
                    type: 'bot',
                    content: 'Thinking...',
                    timestamp: new Date()
                  }} />
                </div>
              )}
              <div ref={messagesEndRef}/>
            </div>
          </div>
        </div>
        <ChatInput onSendClick={handleSendButton} disabled={isLoading}></ChatInput>
      </div>
    </div>
  );
}