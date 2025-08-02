import { motion } from 'framer-motion'
import { MessageCircle, RotateCw } from 'lucide-react'

const Header = () => {

  const handleRefresh = ()=>
  {
    window.location.reload();
  }
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

    <button className='refresh-button' onClick={handleRefresh} title='Start a new chat'>
      <RotateCw size={'1.25rem'}>
      </RotateCw>
    </button>
    </div>
  )
}

export default Header
