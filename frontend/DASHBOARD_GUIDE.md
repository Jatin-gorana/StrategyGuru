# Dashboard Guide

The Trading Strategy Backtester Dashboard provides comprehensive visualization and analysis of backtest results.

## Dashboard Features

### 1. Overview Tab

The main dashboard view displaying all key metrics and charts.

#### Performance Metrics Cards

Four key metrics displayed at the top:

- **Total Return**: Absolute profit/loss and percentage return
  - Shows final equity value
  - Color-coded (green for positive, red for negative)

- **Sharpe Ratio**: Risk-adjusted return metric
  - Higher is better (>1 is good)
  - Indicates return per unit of risk

- **Max Drawdown**: Largest peak-to-trough decline
  - Shown as percentage
  - Indicates maximum loss from peak

- **Win Rate**: Percentage of profitable trades
  - Shows winning vs total trades
  - Higher is better (>50% is good)

#### Charts

**Equity Curve Chart**
- Shows portfolio value over time
- Blue line: Portfolio equity
- Gray dashed line: Initial capital
- Interactive tooltip on hover
- Automatically samples data for large datasets

**Monthly Performance Chart**
- Stacked bar chart showing wins/losses per month
- Green bars: Winning trades
- Red bars: Losing trades
- Hover to see monthly profit

**Drawdown Analysis Chart**
- Area chart showing drawdown percentage over time
- Red area: Drawdown from peak
- Helps identify periods of losses

#### Summary Statistics

Two summary panels:

**Performance Summary**
- Initial capital
- Final equity
- Total profit/loss
- Return percentage

**Risk Metrics**
- Maximum drawdown
- Sharpe ratio
- Win rate
- Profit factor

#### Trade Statistics

Three cards showing:
- **Total Trades**: Number of trades and win/loss breakdown
- **Profit Factor**: Ratio of gross profit to gross loss
- **Avg Win/Loss**: Average profit per winning trade vs average loss

### 2. Trades Tab

Detailed table of all executed trades with sorting and pagination.

#### Trade Table Columns

- **Entry Date**: When the trade was entered
- **Entry Price**: Price at entry
- **Exit Date**: When the trade was exited
- **Exit Price**: Price at exit
- **Qty**: Number of shares traded
- **P&L**: Profit or loss in dollars
- **Return %**: Return percentage

#### Features

- **Sortable Columns**: Click column headers to sort
- **Pagination**: Navigate through trades (10 per page)
- **Color Coding**: Green for profits, red for losses
- **Ascending/Descending**: Toggle sort direction

### 3. Analysis Tab

Advanced metrics and analysis of trading performance.

#### Analysis Metrics

**Return Distribution**
- Visual progress bar showing win rate
- Percentage of winning trades

**Risk/Reward Ratio**
- Ratio of average win to average loss
- Higher is better (>1:1 is good)

**Consecutive Wins**
- Maximum consecutive winning trades
- Indicates strategy consistency

**Consecutive Losses**
- Maximum consecutive losing trades
- Indicates drawdown periods

#### Trade Analysis

**Best Trade**
- Largest single trade profit
- Shows strategy's best case

**Worst Trade**
- Largest single trade loss
- Shows strategy's worst case

**Avg Trade Duration**
- Average number of days per trade
- Indicates holding period

**Expectancy**
- Average profit per trade
- Key metric for strategy viability

## Metrics Explained

### Total Return
```
Total Return = Final Equity - Initial Capital
Total Return % = (Total Return / Initial Capital) × 100
```

### Sharpe Ratio
```
Sharpe Ratio = (Mean Return - Risk-Free Rate) / Standard Deviation × √252
```
- Measures risk-adjusted return
- Higher is better
- >1 is considered good
- >2 is excellent

### Maximum Drawdown
```
Max Drawdown = (Trough Value - Peak Value) / Peak Value × 100
```
- Largest peak-to-trough decline
- Indicates worst-case scenario
- Important for risk management

### Win Rate
```
Win Rate = (Winning Trades / Total Trades) × 100
```
- Percentage of profitable trades
- >50% is generally good
- Combined with profit factor for strategy quality

### Profit Factor
```
Profit Factor = Gross Profit / Gross Loss
```
- Ratio of total wins to total losses
- >1 means profitable
- >2 is very good
- >3 is excellent

## Navigation

### Header Controls

- **Back Button**: Return to home page
- **Export Button**: Download results as JSON
- **New Backtest Button**: Run another backtest

### Tab Navigation

- **Overview**: Main dashboard with all metrics
- **Trades**: Detailed trade history
- **Analysis**: Advanced performance analysis

## Data Export

Click the "Export" button to download backtest results as JSON file.

Exported data includes:
- Strategy text
- Stock symbol
- Date range
- Initial capital
- Final equity
- All metrics
- Complete trade list
- Timestamp

## Tips for Using the Dashboard

1. **Review Equity Curve**: Look for smooth growth vs sharp drawdowns
2. **Check Win Rate**: Aim for >50% win rate
3. **Analyze Drawdown**: Ensure max drawdown is acceptable
4. **Examine Trades**: Review individual trades for patterns
5. **Compare Metrics**: Use multiple metrics to evaluate strategy
6. **Export Results**: Save results for comparison with other strategies

## Performance Interpretation

### Excellent Strategy
- Total Return: >20% annually
- Sharpe Ratio: >2
- Max Drawdown: <10%
- Win Rate: >60%
- Profit Factor: >3

### Good Strategy
- Total Return: 10-20% annually
- Sharpe Ratio: 1-2
- Max Drawdown: 10-20%
- Win Rate: 50-60%
- Profit Factor: 2-3

### Acceptable Strategy
- Total Return: 5-10% annually
- Sharpe Ratio: 0.5-1
- Max Drawdown: 20-30%
- Win Rate: 45-50%
- Profit Factor: 1.5-2

### Poor Strategy
- Total Return: <5% annually
- Sharpe Ratio: <0.5
- Max Drawdown: >30%
- Win Rate: <45%
- Profit Factor: <1.5

## Common Issues

### No Data Displayed
- Ensure backtest completed successfully
- Check browser console for errors
- Try running backtest again

### Charts Not Loading
- Verify data is available
- Check browser compatibility
- Clear browser cache

### Export Not Working
- Check browser download settings
- Ensure pop-ups are not blocked
- Try different browser

## Best Practices

1. **Test Multiple Strategies**: Compare different approaches
2. **Use Realistic Parameters**: Set capital and dates appropriately
3. **Review All Metrics**: Don't rely on single metric
4. **Check Trade Details**: Understand individual trade logic
5. **Validate Results**: Compare with other backtesting tools
6. **Document Findings**: Keep records of tested strategies

## Keyboard Shortcuts

- **Tab Navigation**: Use arrow keys to navigate tabs
- **Sort Tables**: Click column headers to sort
- **Pagination**: Use Previous/Next buttons

## Mobile Responsiveness

Dashboard is fully responsive:
- **Desktop**: Full layout with all features
- **Tablet**: Optimized grid layout
- **Mobile**: Stacked layout with scrolling

## Performance Notes

- Large datasets (>1000 trades) may take longer to render
- Charts automatically sample data for performance
- Export may take a few seconds for large datasets
- Dashboard caches data in SessionStorage

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check browser console for errors
4. Verify backend is running
