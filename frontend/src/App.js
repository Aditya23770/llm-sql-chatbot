import React, { useState } from 'react';
import './App.css';

function App() {
  // State variables to manage the component's data
  const [query, setQuery] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Handles the form submission
  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevents the default form submission behavior
    setIsLoading(true);
    setError('');
    setSqlQuery('');
    setResults([]);

    try {
      // Sends a POST request to the FastAPI backend
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        // Handles HTTP errors from the backend
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An unknown error occurred');
      }

      // Parses the successful JSON response
      const data = await response.json();
      setSqlQuery(data.sql_query);
      setResults(data.results);

    } catch (err) {
      // Catches network errors or errors thrown from the response handling
      setError(err.message);
    } finally {
      // Ensures loading is set to false after the request is complete
      setIsLoading(false);
    }
  };

  // Renders the results in a table format
  const renderTable = () => {
    if (results.length === 0) {
      return <p>No results found.</p>;
    }

    // Gets the column headers from the first result object
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
        <h1>LLM-Powered SQL Chatbot</h1>
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
