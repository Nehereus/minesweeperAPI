const express = require('express');
const path = require('path');

// Create an Express app
const app = express();
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*'); // Allow all origins
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'); // Allow specific methods
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization'); // Allow specific headers
    next();
});
// Serve static files from the current directory (or a 'public' folder)
app.use(express.static(__dirname));

// If you'd rather use a subdirectory like 'public', do:
// app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  // Serve the index.html file by default
  res.sendFile(path.join(__dirname, 'index.html'));
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Node server is running at http://localhost:${PORT}`);
});
