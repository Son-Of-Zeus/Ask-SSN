'use client';
import { useRef } from "react";
import { useEffect, useState } from "react";
import Image from "next/image";
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import './App.css'
import ChatMessage from './components/ChatMessage'
import { Loader2, Bot, User} from "lucide-react";

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
      const query = [...messages, userMessage].map(message => ({
        role: message.type,
        content: message.content
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      console.log('Success:', data);
      const botMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: data.response,
        timestamp: new Date()
      };

      // Add bot response
      setMessages(prevMessages => [...prevMessages, botMessage]);
      console.log(messages);
      
    } catch (error) {
      console.error('Error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: "assistant",
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
                <div className="message assistant-message">
                  <div className="message-avatar">
                    <Bot size={"1.25rem"} className="avatar-icon" />
                  </div>
                  <div className="loading-icon-container">
                    <Loader2 size={"1.5rem"} className="loading-spinner" />
                  </div>
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