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

export const api = {
  runBacktest: async (request: BacktestRequest): Promise<BacktestResponse> => {
    const response = await apiClient.post('/api/backtest', request)
    return response.data
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
      const response = await apiClient.post('/api/backtest/improve-strategy', {
        strategy_text: strategyText,
        metrics: metrics,
        trades_count: tradesCount,
      })
      return response.data
    } catch (error: any) {
      // Handle error response
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
