import { motion } from 'framer-motion'
import { MessageCircle } from 'lucide-react'

const Header = () => {
  return (
    <div
      className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <div className="logo">
          <h1>ASK</h1>
          <img src="/logo.png" height="10%" width = "10%"/>
          
        </div>
        <div className="header-subtitle">
          Your AI Assistant for SSN Related Queries
        </div>
      </div>
    </div>
  )
}

export default Header
