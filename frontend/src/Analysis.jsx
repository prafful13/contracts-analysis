
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './Analysis.css';

const Analysis = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    fetch('/ANALYSIS.md')
      .then(response => response.text())
      .then(text => setMarkdown(text));
  }, []);

  return (
    <div className="analysis-container">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
};

export default Analysis;
