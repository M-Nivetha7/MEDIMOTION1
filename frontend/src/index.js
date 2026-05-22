// This file is intentionally minimal - the actual app is in public/index.html
// We're just mounting a simple div to avoid React errors
import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  return (
    <div style={{ minHeight: '100vh' }}>
      {/* The actual content is loaded from public/index.html */}
      <iframe 
        src="/index.html" 
        style={{ width: '100%', height: '100vh', border: 'none' }}
        title="MediMotion"
      />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
