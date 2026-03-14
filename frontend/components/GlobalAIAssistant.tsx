'use client'

import { useState, useRef, useEffect } from 'react'
import { Bot, X, Maximize2, Minimize2, Loader2, Play } from 'lucide-react'
import { api, ChatMessage } from '@/lib/api'

/** Renders agent messages with beautiful formatting:
 * - ALL-CAPS section headers become accent-colored labels
 * - Numbers and percentages get highlighted green chips
 * - Lines become stacked readable paragraphs
 */
function AgentMessage({ content }: { content: string }) {
  const lines = content.split('\n').filter(l => l.trim() !== '')

  // Regex: highlight numbers with optional % or $ prefix
  const highlightNumbers = (text: string) => {
    const parts = text.split(/(\$?-?\d+(?:[.,]\d+)*%?)/g)
    return parts.map((part, i) =>
      /^\$?-?\d+(?:[.,]\d+)*%?$/.test(part) ? (
        <span key={i} className="inline-block bg-accent/10 text-accent font-mono font-semibold px-1.5 py-0.5 rounded text-xs mx-0.5 border border-accent/20">
          {part}
        </span>
      ) : part
    )
  }

  return (
    <div className="space-y-2.5">
      {lines.map((line, idx) => {
        const trimmed = line.trim()

        // Detect ALL-CAPS header like "ANALYSIS:" or "ACTION ITEM:"
        const headerMatch = trimmed.match(/^([A-Z][A-Z\s]+):(.*)$/)
        if (headerMatch) {
          const label = headerMatch[1].trim()
          const rest = headerMatch[2].trim()
          return (
            <div key={idx}>
              <span className="inline-block text-[10px] font-bold text-accent uppercase tracking-widest border-b border-accent/30 pb-0.5 mb-1">
                {label}
              </span>
              {rest && (
                <p className="text-sm text-slate-300 leading-relaxed mt-0.5">
                  {highlightNumbers(rest)}
                </p>
              )}
            </div>
          )
        }

        // Numbered list items like "1. something"
        const numberedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/)
        if (numberedMatch) {
          return (
            <div key={idx} className="flex gap-2 items-start">
              <span className="shrink-0 w-5 h-5 rounded-full bg-accent/10 text-accent text-[10px] font-bold flex items-center justify-center mt-0.5 border border-accent/20">
                {numberedMatch[1]}
              </span>
              <p className="text-sm text-slate-300 leading-relaxed">
                {highlightNumbers(numberedMatch[2])}
              </p>
            </div>
          )
        }

        // Regular paragraph
        return (
          <p key={idx} className="text-sm text-slate-300 leading-relaxed">
            {highlightNumbers(trimmed)}
          </p>
        )
      })}
    </div>
  )
}


export default function GlobalAIAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  
  const [messages, setMessages] = useState<ChatMessage[]>([{
    role: 'assistant',
    content: 'Quant Agent initialized. I can analyze your strategies, suggest optimizations based on volatility regimes, or run mock portfolio backtests.'
  }])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMsg: ChatMessage = { role: 'user', content: inputMessage.trim() }
    
    setMessages(prev => [...prev, userMsg])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Build context from session storage if available
      let contextData = ''
      try {
        const resultsData = sessionStorage.getItem('backtest_results')
        const paramsData = sessionStorage.getItem('backtest_params')
        if (resultsData && paramsData) {
          const results = JSON.parse(resultsData)
          const params = JSON.parse(paramsData)
          
          // Truncate equity curve and trades heavily to fit inside context window
          delete results.equity_curve
          if (results.trades && results.trades.length > 50) {
            results.trades = results.trades.slice(0, 50)
            results.trades_note = "Only showing last 50 trades due to context limits."
          }

          contextData = JSON.stringify({
            strategy_parameters: params,
            backtest_results: results
          }, null, 2)
        }
      } catch (e) {
        console.error('Failed to parse session context for AI Agent', e)
      }

      // Pass the conversation history (omitting the first system welcome msg to save token limits if you prefer, or pass all)
      const chatHistory = [...messages, userMsg].filter(m => m.role !== 'system')
      
      const response = await api.chat(chatHistory, contextData)
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response
      }])
    } catch (error) {
      console.error('Failed to get AI response:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I encountered an error connecting to the quant matrix. Please check your API keys and try again.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-secondary border border-accent/30 text-accent p-3 rounded-full shadow-[0_0_15px_rgba(0,255,136,0.3)] hover:shadow-[0_0_25px_rgba(0,255,136,0.5)] transition-all flex items-center justify-center group"
      >
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse border-2 border-primary"></span>
        <Bot className="w-6 h-6 group-hover:scale-110 transition-transform" />
      </button>
    )
  }

  return (
    <div
      className={`fixed top-0 right-0 h-full bg-primary/95 backdrop-blur-md border-l border-slate-800 z-50 flex flex-col transition-all duration-300 shadow-2xl ${
        isExpanded ? 'w-full md:w-[600px]' : 'w-full md:w-[350px]'
      }`}
    >
      {/* Header */}
      <div className="h-14 border-b border-slate-800 flex items-center justify-between px-4 shrink-0 bg-[#0B0E14]">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-accent" />
          <h2 className="text-xs font-bold text-white tracking-wider">AI QUANT AGENT</h2>
          <span className="w-2 h-2 rounded-full bg-accent/80 animate-pulse ml-2"></span>
        </div>
        <div className="flex items-center gap-2 text-slate-500">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 hover:bg-slate-800 rounded transition-colors hidden md:block"
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 hover:bg-slate-800 rounded hover:text-red-400 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((message, idx) => (
          <div key={idx} className={message.role === 'user' ? 'flex justify-end' : ''}>
            <div className={
              message.role === 'user'
                ? 'bg-accent/10 border border-accent/20 rounded-lg p-3 max-w-[85%]'
                : 'bg-secondary border border-slate-800 rounded-lg p-4'
            }>
               {message.role !== 'user' && (
                  <span className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-1 mb-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent/50 filter brightness-200"></span> 
                    AGENT
                  </span>
               )}
               {message.role === 'user' ? (
                 <p className="text-sm text-white">{message.content}</p>
               ) : (
                 <AgentMessage content={message.content} />
               )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="bg-secondary border border-slate-800 rounded-lg p-4">
             <span className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-1 mb-2">
               <span className="w-1.5 h-1.5 rounded-full bg-accent/50 filter brightness-200"></span> 
               AGENT
             </span>
             <div className="flex items-center gap-2 text-slate-400">
               <Loader2 className="w-4 h-4 animate-spin" />
               <span className="text-sm">Analyzing sequence...</span>
             </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-800 mt-auto shrink-0 bg-[#0B0E14]">
        <div className="flex gap-2 mb-3 overflow-x-auto custom-scrollbar pb-1">
          {[
            "Analyze and improve my strategy",
            "What was my worst trade and why?",
            "How to reduce my max drawdown?",
            "Suggest better exit rules",
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => setInputMessage(prompt)}
              className="text-[10px] whitespace-nowrap bg-secondary border border-slate-700 px-2 py-1.5 rounded text-slate-400 hover:text-accent hover:border-accent/40 cursor-pointer transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="relative flex items-center">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSendMessage()
            }}
            placeholder="Command your agent..."
            className="w-full bg-secondary border border-slate-700 rounded-lg py-3 pl-4 pr-12 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 font-mono"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="absolute right-2 p-1.5 text-slate-500 hover:text-accent transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
          </button>
        </div>
      </div>
    </div>
  )
}
