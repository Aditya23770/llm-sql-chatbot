import React, { useState } from 'react';
import './App.css';

// IMPORTANT: In a real production app, this key should not be hardcoded.
// It would typically be stored in an environment variable.
const API_KEY = "MY_SUPER_SECRET_API_KEY";

function App() {
  const [query, setQuery] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setSqlQuery('');
    setResults([]);

    try {
      // Sends a POST request to the FastAPI backend with the API key in the header.
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY, // Adds the API key to the request header
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        // Handles both regular errors and authentication errors
        throw new Error(errorData.detail || 'An unknown error occurred');
      }

      const data = await response.json();
      setSqlQuery(data.sql_query);
      setResults(data.results);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTable = () => {
    if (results.length === 0) {
      return <p>No results found.</p>;
    }

    const headers = Object.keys(results[0]);

    return (
      <table>
        <thead>
          <tr>
            {headers.map(header => <th key={header}>{header}</th>)}
          </tr>
        </thead>
        <tbody>
          {results.map((row, index) => (
            <tr key={index}>
              {headers.map(header => <td key={header}>{row[header]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Data-Whisperer</h1>
        <p>Enter a natural language query about the customer database.</p>
      </header>
      <main>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Show me all male customers from Delhi"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Submit Query'}
          </button>
        </form>

        {error && <div className="error-message">Error: {error}</div>}

        {sqlQuery && (
          <div className="result-section">
            <h2>Generated SQL Query:</h2>
            <pre><code>{sqlQuery}</code></pre>
          </div>
        )}

        {results.length > 0 && (
          <div className="result-section">
            <h2>Query Results:</h2>
            {renderTable()}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
