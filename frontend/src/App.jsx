import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { ChevronsUpDown, ServerCrash, SlidersHorizontal, Info, ArrowLeft, ArrowRight, BookOpen, BarChart2 } from 'lucide-react';
import { DEFAULT_PARAMS } from './config.js'; // Import default parameters
import Analysis from './Analysis.jsx';

// --- Helper Components ---

const Card = ({ children, className = '' }) => (
  <div className={`bg-white dark:bg-gray-800/50 rounded-xl shadow-lg backdrop-blur-sm border border-gray-200 dark:border-gray-700 ${className}`}>
    {children}
  </div>
);

const Button = ({ children, onClick, className = '', isLoading = false }) => (
  <button
    onClick={onClick}
    disabled={isLoading}
    className={`w-full flex items-center justify-center px-6 py-3 text-base font-semibold text-white rounded-lg shadow-md transition-all duration-300 ease-in-out bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400 disabled:cursor-not-allowed ${className}`}
  >
    {isLoading ? (
      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    ) : children}
  </button>
);

const InputGroup = ({ label, children }) => (
  <div className="flex flex-col space-y-2">
    <label className="text-sm font-medium text-gray-600 dark:text-gray-300">{label}</label>
    {children}
  </div>
);

const TextInput = ({ value, onChange }) => (
  <input
    type="text"
    value={value}
    onChange={onChange}
    className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-indigo-500 focus:border-indigo-500 transition"
    placeholder="e.g., AAPL,MSFT,GOOGL"
  />
);

const NumberInput = ({ value, onChange, name }) => (
  <input
    type="number"
    name={name}
    value={value}
    onChange={onChange}
    className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-indigo-500 focus:border-indigo-500 transition"
    step="0.01"
  />
);

// --- Main Components ---

const ScreenerTypeSelector = ({ screenerType, setScreenerType }) => (
  <div className="flex justify-center mb-6">
    <div className="flex space-x-2 p-1 bg-gray-200 dark:bg-gray-700/50 rounded-lg">
      <button
        onClick={() => setScreenerType('income')}
        className={`px-4 py-2 text-sm font-semibold rounded-md transition-colors ${screenerType === 'income' ? 'bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-300 shadow' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/50'}`}
      >
        💰 Income Screener
      </button>
      <button
        onClick={() => setScreenerType('buy')}
        className={`px-4 py-2 text-sm font-semibold rounded-md transition-colors ${screenerType === 'buy' ? 'bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-300 shadow' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/50'}`}
      >
        📈 Buy Screener
      </button>
    </div>
  </div>
);

const Controls = ({ params, setParams, onAnalyze, isLoading }) => {
  const handleTickerChange = (e, type) => {
    setParams(p => ({ ...p, [type]: e.target.value.toUpperCase().split(',').map(t => t.trim()).join(',') }));
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    const numericValue = value === '' ? '' : parseFloat(value);
    
    if (value !== '' && isNaN(numericValue)) {
        return; 
    }

    setParams(p => ({
      ...p,
      filters: { ...p.filters, [name]: numericValue }
    }));
  };

  const setScreenerType = (type) => {
    setParams(p => ({ ...p, screenerType: type }));
  };

  return (
    <Card className="p-6">
      <ScreenerTypeSelector screenerType={params.screenerType} setScreenerType={setScreenerType} />
      <div className="flex items-center mb-4 text-xl font-bold text-gray-800 dark:text-white">
        <SlidersHorizontal className="mr-3 text-indigo-500" />
        Analysis Controls
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {params.screenerType === 'income' ? (
          <>
            <InputGroup label="Put Tickers (Stocks to Buy)">
              <TextInput value={params.putTickers} onChange={(e) => handleTickerChange(e, 'putTickers')} />
            </InputGroup>
            <InputGroup label="Call Tickers (Stocks Owned)">
              <TextInput value={params.callTickers} onChange={(e) => handleTickerChange(e, 'callTickers')} />
            </InputGroup>
          </>
        ) : (
          <div className="md:col-span-2">
            <InputGroup label="Tickers to Analyze">
              <TextInput value={params.putTickers} onChange={(e) => handleTickerChange(e, 'putTickers')} />
            </InputGroup>
          </div>
        )}

        <div className="md:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
          <InputGroup label="Min DTE">
            <NumberInput name="DTE_MIN" value={params.filters.DTE_MIN} onChange={handleFilterChange} />
          </InputGroup>
          <InputGroup label="Max DTE">
            <NumberInput name="DTE_MAX" value={params.filters.DTE_MAX} onChange={handleFilterChange} />
          </InputGroup>
          <InputGroup label="Min Volume">
            <NumberInput name="MIN_VOLUME" value={params.filters.MIN_VOLUME} onChange={handleFilterChange} />
          </InputGroup>
          <InputGroup label="Min Open Int.">
            <NumberInput name="MIN_OPEN_INTEREST" value={params.filters.MIN_OPEN_INTEREST} onChange={handleFilterChange} />
          </InputGroup>
        </div>

        {params.screenerType === 'income' ? (
          <>
            <div className="p-4 bg-indigo-50 dark:bg-gray-700/50 rounded-lg md:col-span-2">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">Primary Filter (Market Hours)</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <InputGroup label="Put Δ Min">
                  <NumberInput name="PUT_DELTA_MIN" value={params.filters.PUT_DELTA_MIN} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Put Δ Max">
                  <NumberInput name="PUT_DELTA_MAX" value={params.filters.PUT_DELTA_MAX} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Call Δ Min">
                  <NumberInput name="CALL_DELTA_MIN" value={params.filters.CALL_DELTA_MIN} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Call Δ Max">
                  <NumberInput name="CALL_DELTA_MAX" value={params.filters.CALL_DELTA_MAX} onChange={handleFilterChange} />
                </InputGroup>
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg md:col-span-2">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">Fallback Filter (After Hours)</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <InputGroup label="Put OTM% Min">
                  <NumberInput name="PUT_OTM_PERCENT_MIN" value={params.filters.PUT_OTM_PERCENT_MIN} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Put OTM% Max">
                  <NumberInput name="PUT_OTM_PERCENT_MAX" value={params.filters.PUT_OTM_PERCENT_MAX} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Call OTM% Min">
                  <NumberInput name="CALL_OTM_PERCENT_MIN" value={params.filters.CALL_OTM_PERCENT_MIN} onChange={handleFilterChange} />
                </InputGroup>
                <InputGroup label="Call OTM% Max">
                  <NumberInput name="CALL_OTM_PERCENT_MAX" value={params.filters.CALL_OTM_PERCENT_MAX} onChange={handleFilterChange} />
                </InputGroup>
              </div>
            </div>
          </>
        ) : (
          <div className="p-4 bg-indigo-50 dark:bg-gray-700/50 rounded-lg md:col-span-2">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">Buy Screener Filters</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <InputGroup label="Call Δ Min">
                <NumberInput name="BUY_CALL_DELTA_MIN" value={params.filters.BUY_CALL_DELTA_MIN} onChange={handleFilterChange} />
              </InputGroup>
              <InputGroup label="Call Δ Max">
                <NumberInput name="BUY_CALL_DELTA_MAX" value={params.filters.BUY_CALL_DELTA_MAX} onChange={handleFilterChange} />
              </InputGroup>
              <InputGroup label="Put Δ Min">
                <NumberInput name="BUY_PUT_DELTA_MIN" value={params.filters.BUY_PUT_DELTA_MIN} onChange={handleFilterChange} />
              </InputGroup>
              <InputGroup label="Put Δ Max">
                <NumberInput name="BUY_PUT_DELTA_MAX" value={params.filters.BUY_PUT_DELTA_MAX} onChange={handleFilterChange} />
              </InputGroup>
            </div>
          </div>
        )}
      </div>
      <div className="mt-6">
        <Button onClick={onAnalyze} isLoading={isLoading}>
          {isLoading ? 'Analyzing...' : `Run ${params.screenerType === 'income' ? 'Income' : 'Buy'} Analysis`}
        </Button>
      </div>
    </Card>
  );
};

const PaginationControls = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 border-t dark:border-gray-700">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Previous
      </button>
      <span className="text-sm text-gray-700 dark:text-gray-300">
        Page {currentPage} of {totalPages}
      </span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
      >
        Next
        <ArrowRight className="w-4 h-4 ml-2" />
      </button>
    </div>
  );
};

const OptionsTable = ({ title, data, defaultSort, type, headers }) => {
  const [sortConfig, setSortConfig] = useState(defaultSort);
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  useEffect(() => {
    setCurrentPage(1);
  }, [data]);

  const sortedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    let sortableData = [...data];
    if (sortConfig.key) {
      sortableData.sort((a, b) => {
        const valA = a[sortConfig.key] || 0;
        const valB = b[sortConfig.key] || 0;
        if (valA < valB) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (valA > valB) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableData;
  }, [data, sortConfig]);

  const totalPages = Math.ceil(sortedData.length / rowsPerPage);
  const paginatedData = sortedData.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
    setCurrentPage(1);
  };

  if (!data) return null;

  return (
    <Card className="mt-8 overflow-hidden">
      <h2 className={`text-xl font-bold p-4 ${type === 'put' ? 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-200' : 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-200'}`}>
        {title}
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              {headers.map(h => (
                <th key={h.key} scope="col" className="px-4 py-3 cursor-pointer" onClick={() => requestSort(h.key)}>
                  <div className="flex items-center">
                    {h.label}
                    <ChevronsUpDown className="w-4 h-4 ml-1.5" />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr key={index} className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600/50">
                {headers.map(h => (
                  <td key={h.key} className="px-4 py-3 font-medium text-gray-900 dark:text-white whitespace-nowrap">
                    {typeof row[h.key] === 'number' ? row[h.key].toFixed(2) : row[h.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length === 0 && <p className="p-4 text-center text-gray-500 dark:text-gray-400">No suitable contracts found with the current criteria.</p>}
      <PaginationControls currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} />
    </Card>
  );
};

const Legend = () => (
    <Card className="mt-8 p-6">
        <div className="flex items-center mb-4 text-xl font-bold text-gray-800 dark:text-white">
            <Info className="mr-3 text-indigo-500" />
            How to Read the Results
        </div>
        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300 list-disc list-inside">
            <li><strong>DTE:</strong> Days To Expiration. Lower DTE means faster time decay (theta).</li>
            <li><strong>Premium:</strong> Cash received per share. Higher is better.</li>
            <li><strong>Delta:</strong> Approx. probability of expiring in-the-money. Lower is safer for selling.</li>
            <li><strong>OTM %:</strong> How far the strike is from the stock price. Higher is safer.</li>
            <li><strong>IV (Implied Volatility):</strong> Market's expectation of price swings. Higher IV = higher premium/risk.</li>
            <li><strong>Weekly/Annual %:</strong> Your return on collateral, normalized. Higher is better.</li>
            <li><strong>Collateral:</strong> Total cash required to secure the trade (per 100 shares).</li>
        </ul>
    </Card>
);

const TabButton = ({ children, onClick, isActive }) => (
  <button
    onClick={onClick}
    className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${isActive
        ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300'
        : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'}`}>
    {children}
  </button>
);

export default function App() {
  // Use the imported object for the initial state
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [results, setResults] = useState({ puts: null, calls: null, bullish_calls: null, bearish_puts: null });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('screener'); // 'screener' or 'analysis'

  const analyze = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    // For "buy" screener, combine tickers
    let apiParams = { ...params };
    if (params.screenerType === 'buy') {
      const allTickers = [...params.putTickers.split(','), ...params.callTickers.split(',')].filter(t => t).join(',');
      apiParams = { ...apiParams, putTickers: allTickers, callTickers: '' };
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiParams),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);

    } catch (e) {
      setError("Failed to fetch data from the backend. Is the Python server running?");
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [params]);

  const renderResults = () => {
    const incomeHeaders = [
      { key: 'ticker', label: 'Ticker' },
      { key: 'expirationDate', label: 'Expiry' },
      { key: 'DTE', label: 'DTE' },
      { key: 'strike', label: 'Strike' },
      { key: 'currentPrice', label: 'Stock Price' },
      { key: 'premium', label: 'Premium' },
      { key: 'delta', label: 'Delta' },
      { key: 'otmPercent', label: 'OTM %' },
      { key: 'impliedVolatility', label: 'IV' },
      { key: 'weeklyReturn', label: 'Weekly %' },
      { key: 'annualizedReturn', label: 'Annual %' },
      { key: 'collateral', label: 'Collateral' },
    ];

    const buyHeaders = [
      { key: 'buyScore', label: 'Buy Score' },
      { key: 'ticker', label: 'Ticker' },
      { key: 'expirationDate', label: 'Expiry' },
      { key: 'DTE', label: 'DTE' },
      { key: 'strike', label: 'Strike' },
      { key: 'currentPrice', label: 'Stock Price' },
      { key: 'premium', label: 'Premium' },
      { key: 'delta', label: 'Delta' },
      { key: 'impliedVolatility', label: 'IV' },
      { key: 'volume', label: 'Volume' },
      { key: 'openInterest', label: 'Open Int.' },
    ];

    if (params.screenerType === 'income') {
      return (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-3">
              <OptionsTable title="💰 Best Cash-Secured Puts to Sell" data={results.puts} defaultSort={{ key: 'annualizedReturn', direction: 'descending' }} type="call" headers={incomeHeaders} />
            </div>
            <div className="lg:col-span-3">
              <OptionsTable title="📈 Best Covered Calls to Sell" data={results.calls} defaultSort={{ key: 'annualizedReturn', direction: 'descending' }} type="put" headers={incomeHeaders} />
            </div>
          </div>
          <Legend />
        </>
      );
    } else {
      return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-3">
                  <OptionsTable title="📈 Bullish Opportunities (Calls to Buy)" data={results.bullish_calls} defaultSort={{ key: 'buyScore', direction: 'descending' }} type="call" headers={buyHeaders} />
              </div>
              <div className="lg:col-span-3">
                  <OptionsTable title="📉 Bearish Opportunities (Puts to Buy)" data={results.bearish_puts} defaultSort={{ key: 'buyScore', direction: 'descending' }} type="put" headers={buyHeaders} />
              </div>
          </div>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800 dark:text-white tracking-tight">
            Options <span className="text-indigo-600 dark:text-indigo-400">Screener</span>
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Find the best options contracts based on your custom criteria.
          </p>
        </header>

        <div className="flex justify-center mb-8">
          <div className="flex space-x-2 p-1 bg-gray-200 dark:bg-gray-700/50 rounded-lg">
            <TabButton onClick={() => setActiveTab('screener')} isActive={activeTab === 'screener'}>
              <BarChart2 className="w-4 h-4 mr-2" />
              Screener
            </TabButton>
            <TabButton onClick={() => setActiveTab('analysis')} isActive={activeTab === 'analysis'}>
              <BookOpen className="w-4 h-4 mr-2" />
              Analysis
            </TabButton>
          </div>
        </div>

        <main>
          {activeTab === 'screener' ? (
            <>
              <Controls params={params} setParams={setParams} onAnalyze={analyze} isLoading={isLoading} />
              
              {error && (
                <Card className="mt-8 p-4 bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-200 flex items-center">
                  <ServerCrash className="w-6 h-6 mr-3" />
                  <p>{error}</p>
                </Card>
              )}

              {renderResults()}
            </>
          ) : (
            <Card className="p-6">
              <Analysis />
            </Card>
          )}
        </main>
        
        <footer className="text-center mt-12 text-xs text-gray-500 dark:text-gray-400">
          <p>Disclaimer: This tool is for educational and informational purposes only. Not financial advice.</p>
          <p>Data is fetched from Yahoo Finance and may be delayed.</p>
        </footer>
      </div>
    </div>
  );
}
