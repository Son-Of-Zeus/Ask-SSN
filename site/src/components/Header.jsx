import { motion } from 'framer-motion'
import { MessageCircle } from 'lucide-react'

const Header = () => {
  return (
    <motion.header 
      className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <div className="logo">
          <MessageCircle size={32} className="logo-icon" />
          <h1>ASK SSN</h1>
        </div>
        <div className="header-subtitle">
          Your AI Assistant for SSN Related Queries
        </div>
      </div>
    </motion.header>
  )
}

export default Header
