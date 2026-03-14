import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface BacktestRequest {
  strategy_text: string
  stock_symbol: string
  start_date: string
  end_date: string
  initial_capital?: number
}

export interface Trade {
  entry_date: string
  entry_price: number
  exit_date: string
  exit_price: number
  quantity: number
  pnl: number
  pnl_percent: number
}

export interface EquityCurvePoint {
  date: string
  equity: number
}

export interface BacktestMetrics {
  total_return: number
  total_return_percent: number
  sharpe_ratio: number
  max_drawdown: number
  max_drawdown_percent: number
  win_rate: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  avg_win: number
  avg_loss: number
  profit_factor: number
}

export interface StrategyImprovement {
  success: boolean
  original_strategy: string
  improved_strategy: string
  improvements: string[]
  reasoning: string
  risk_level: string
}

export interface BacktestResponse {
  success: boolean
  message: string
  trades: Trade[]
  equity_curve: EquityCurvePoint[]
  metrics: BacktestMetrics
}

export interface StrategyExample {
  name: string
  description: string
  strategy: string
  indicators: string[]
  risk_level: string
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
})

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      // Log warning if token is missing for authenticated endpoints
      if (config.url && (config.url.includes('/backtest') || config.url.includes('/users'))) {
        console.warn('No access token found in localStorage for authenticated request:', config.url)
      }
    }
  }
  return config
})

// Handle 401 errors by redirecting to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        window.location.href = '/login?error=session_expired'
      }
    }
    return Promise.reject(error)
  }
)

export const api = {
  // Authentication
  register: async (name: string, email: string, password: string) => {
    const response = await apiClient.post('/api/users/register', {
      name,
      email,
      password,
    })
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  login: async (email: string, password: string) => {
    const response = await apiClient.post('/api/users/login', {
      email,
      password,
    })
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  },

  // User Profile
  getProfile: async () => {
    const response = await apiClient.get('/api/users/profile')
    return response.data
  },

  getStrategies: async () => {
    const response = await apiClient.get('/api/users/strategies')
    return response.data
  },

  getBacktests: async () => {
    const response = await apiClient.get('/api/users/backtests')
    return response.data
  },

  getBacktestDetail: async (backtestId: string) => {
    const response = await apiClient.get(`/api/users/backtests/${backtestId}`)
    return response.data
  },

  runBacktest: async (request: BacktestRequest): Promise<BacktestResponse> => {
    try {
      // Check if user is authenticated
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token')
        if (!token) {
          console.error('No access token found. Redirecting to login.')
          window.location.href = '/login?error=not_authenticated'
          throw new Error('Please login to run backtests')
        }
      }

      console.log('Running backtest with request:', request)
      const response = await apiClient.post('/api/backtest', request)
      console.log('Backtest response received:', response.data)
      return response.data
    } catch (error: any) {
      console.error('Backtest error:', error)
      throw error
    }
  },

  parseStrategy: async (strategyText: string) => {
    const response = await apiClient.post('/api/backtest/parse-strategy', {
      strategy_text: strategyText,
    })
    return response.data
  },

  getIndicators: async () => {
    const response = await apiClient.get('/api/backtest/indicators')
    return response.data
  },

  getExamples: async (): Promise<{ success: boolean; examples: StrategyExample[] }> => {
    const response = await apiClient.get('/api/backtest/examples')
    return response.data
  },

  improveStrategy: async (
    strategyText: string,
    metrics: BacktestMetrics,
    tradesCount: number
  ): Promise<StrategyImprovement> => {
    try {
      // Check if user is authenticated
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token')
        if (!token) {
          console.error('No access token found. Redirecting to login.')
          window.location.href = '/login?error=not_authenticated'
          throw new Error('Please login to improve strategies')
        }
      }

      const response = await apiClient.post('/api/backtest/improve-strategy', {
        strategy_text: strategyText,
        metrics: metrics,
        trades_count: tradesCount,
      })
      console.log('Improve strategy response:', response.data)
      return response.data
    } catch (error: any) {
      // Handle error response
      console.error('Improve strategy error:', error)
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      throw error
    }
  },

  healthCheck: async () => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default api
