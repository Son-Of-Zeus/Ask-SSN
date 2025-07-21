import { motion } from 'framer-motion'
import Header from './components/Header'
import ChatInput from './components/ChatInput'
import './App.css'
import ChatMessage from './components/ChatMessage'

function App() {
  return (
    <div className="app">
      <div className="chat-container">
        <Header />
        
        <div className="messages-container">
          <div className="messages-wrapper">
            <div className="welcome-message">
            </div>
            <div>
              <ChatMessage message={{
                id: 1,
                type: 'user',
                content: 'hi',
                timestamp: new Date()
                }} />
            </div>
              <div>
              <ChatMessage message={{
                id: 1,
                type: 'bot',
                content: 'hello',
                timestamp: new Date()
                }} />
            </div>
            <div>
              <ChatMessage message={{
                id: 1,
                type: 'user',
                content: 'hi',
                timestamp: new Date()
                }} />
            </div>
              <div>
              <ChatMessage message={{
                id: 1,
                type: 'bot',
                content: 'hello',
                timestamp: new Date()
                }} />
            </div>
            <div>
              <ChatMessage message={{
                id: 1,
                type: 'user',
                content: 'hi',
                timestamp: new Date()
                }} />
            </div>
              <div>
              <ChatMessage message={{
                id: 1,
                type: 'bot',
                content: 'hello',
                timestamp: new Date()
                }} />
            </div>
            <div>
              <ChatMessage message={{
                id: 1,
                type: 'user',
                content: 'hi',
                timestamp: new Date()
                }} />
            </div>
              <div>
              <ChatMessage message={{
                id: 1,
                type: 'bot',
                content: 'hello',
                timestamp: new Date()
                }} />
            </div>
          </div>
        </div>

        <ChatInput></ChatInput>
      </div>
    </div>
  )
}

export default App
