# Trading Strategy Backtester - Frontend

A modern Next.js 14 frontend for backtesting trading strategies with real market data.

## Features

- 🎯 **Strategy Input** - Enter trading strategies in natural language
- 📊 **Real-time Charts** - Interactive equity curve visualization
- 📈 **Detailed Metrics** - Sharpe ratio, drawdown, win rate, and more
- 📋 **Trade History** - Sortable table of all executed trades
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS
- ⚡ **Fast Performance** - Built with Next.js 14 App Router

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Language**: TypeScript

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (strategy input)
│   ├── results/
│   │   └── page.tsx        # Results page
│   └── globals.css         # Global styles
├── components/
│   ├── StrategyInput.tsx   # Strategy input form
│   ├── MetricsCard.tsx     # Metric display card
│   ├── EquityChart.tsx     # Equity curve chart
│   └── TradesTable.tsx     # Trades history table
├── lib/
│   └── api.ts              # API client
├── public/                 # Static assets
└── package.json
```

## Installation

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Home Page (`/`)

1. **Enter Strategy**: Type your trading strategy in natural language
   - Example: "Buy when RSI < 30 and sell when RSI > 70"
   - Or click an example strategy to load it

2. **Select Parameters**:
   - Stock symbol (e.g., AAPL, GOOGL)
   - Initial capital (default: $10,000)
   - Date range (start and end dates)

3. **Run Backtest**: Click "Run Backtest" button

4. **View Results**: Automatically redirected to results page

### Results Page (`/results`)

Displays comprehensive backtest results:

- **Key Metrics**:
  - Total return and percentage
  - Sharpe ratio (risk-adjusted return)
  - Maximum drawdown
  - Win rate

- **Equity Curve**: Interactive chart showing portfolio value over time

- **Trade Statistics**:
  - Total trades executed
  - Profit factor
  - Average win/loss

- **Trades Table**: Sortable table with all trade details
  - Entry/exit dates and prices
  - Quantity and P&L
  - Return percentage

- **Download**: Export results as JSON

## Components

### StrategyInput

Handles strategy input and parameter selection.

```tsx
<StrategyInput
  onSubmit={handleSubmit}
  isLoading={isLoading}
  examples={examples}
/>
```

### MetricsCard

Displays a single metric with icon and trend indicator.

```tsx
<MetricsCard
  title="Total Return"
  value="$1,250.50"
  unit="(12.51%)"
  icon={<TrendingUp />}
  trend="up"
/>
```

### EquityChart

Interactive chart showing portfolio equity over time.

```tsx
<EquityChart
  data={equityCurve}
  initialCapital={10000}
/>
```

### TradesTable

Sortable, paginated table of executed trades.

```tsx
<TradesTable trades={trades} />
```

## API Integration

The frontend communicates with the FastAPI backend via the `api` client:

```typescript
import api from '@/lib/api'

// Run backtest
const response = await api.runBacktest({
  strategy_text: "Buy when RSI < 30 and sell when RSI > 70",
  stock_symbol: "AAPL",
  start_date: "2023-01-01",
  end_date: "2024-01-01",
  initial_capital: 10000
})

// Parse strategy
const parsed = await api.parseStrategy(strategyText)

// Get indicators
const indicators = await api.getIndicators()

// Get examples
const examples = await api.getExamples()
```

## Styling

### Tailwind CSS Configuration

Custom colors and animations defined in `tailwind.config.ts`:

- **Primary**: `#0f172a` (dark blue)
- **Secondary**: `#1e293b` (slate)
- **Accent**: `#3b82f6` (blue)
- **Success**: `#10b981` (green)
- **Danger**: `#ef4444` (red)

### Global Styles

Custom CSS in `app/globals.css`:

- Scrollbar styling
- Input focus effects
- Button hover animations
- Loading skeleton

## Performance Optimization

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **CSS Optimization**: Tailwind CSS purging
- **API Caching**: SessionStorage for results
- **Chart Optimization**: Data sampling for large datasets

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Environment Variables

```env
# API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

### Run Development Server

```bash
npm run dev
```

### Build for Production

```bash
npm run build
npm start
```

### Lint Code

```bash
npm run lint
```

## Troubleshooting

### API Connection Error

**Problem**: "Failed to connect to API"

**Solution**:
1. Ensure backend is running on `http://localhost:8000`
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Check browser console for CORS errors

### Results Not Loading

**Problem**: "No results found" on results page

**Solution**:
1. Ensure backtest completed successfully
2. Check browser's SessionStorage is enabled
3. Try running backtest again

### Chart Not Displaying

**Problem**: Equity chart shows "No data available"

**Solution**:
1. Ensure backtest returned equity curve data
2. Check browser console for errors
3. Try different date range

## Best Practices

1. **Test Strategies**: Always backtest before trading
2. **Use Realistic Parameters**: Set capital and dates appropriately
3. **Check Metrics**: Review Sharpe ratio and drawdown
4. **Validate Results**: Compare with other backtesting tools
5. **Monitor Trades**: Review individual trade details

## Future Enhancements

- [ ] Strategy optimization
- [ ] Multiple strategy comparison
- [ ] Advanced charting (candlesticks, indicators)
- [ ] Strategy templates
- [ ] User authentication
- [ ] Save/load strategies
- [ ] Export to CSV/PDF
- [ ] Real-time backtesting

## License

MIT

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review example strategies
3. Check browser console for errors
4. Verify backend is running

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
