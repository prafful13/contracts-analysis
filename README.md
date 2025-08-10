# Options Income Screener Application

## 1. Project Overview

The Options Income Screener is a web-based tool designed for options traders who focus on income-generating strategies like selling cash-secured puts and covered calls. It provides a user-friendly interface to scan the market for potentially profitable contracts based on a variety of customizable criteria.

The application fetches real-time (or last-close) market data and presents the best opportunities in sortable tables, allowing traders to quickly identify contracts that match their specific risk tolerance and return objectives.

---

## 2. Architecture

This application is built on a modern client-server architecture, separating the user interface from the data processing logic.

* **Backend (Python & Flask):** A lightweight Python server built with the Flask framework. Its sole responsibility is to handle the heavy lifting:
    * Receiving analysis requests from the frontend.
    * Using the `yfinance` library to fetch real options data from Yahoo Finance.
    * Filtering and analyzing thousands of contracts based on the user's criteria.
    * Sending the processed data back to the frontend as a clean JSON response.

* **Frontend (React.js & Vite):** A fast, modern single-page application (SPA) built with React and Vite. Its responsibilities are:
    * Providing an interactive and intuitive user interface with forms and controls.
    * Sending the user's parameters to the Python backend via an API call.
    * Receiving the JSON data from the backend.
    * Displaying the results in interactive, sortable tables.

---

## 3. Prerequisites

Before you begin, ensure you have the following software installed on your MacBook:

1.  **Python (3.8 or newer):** You can check by opening a terminal and running `python3 --version`. If not installed, get it from [python.org](https://www.python.org/).
2.  **Node.js (v16 or newer):** This is required to run the React frontend. It includes `npm` (Node Package Manager). You can download it from [nodejs.org](https://nodejs.org/).

---

## 4. Local Setup and Installation

To run the application locally, you will need to set up and run the backend and frontend in two separate terminal windows.

### Backend Setup (Terminal 1)

1.  **Navigate to your main project folder** (e.g., `contracts-analysis`).
2.  **Save the Backend File:** Ensure the Python Flask code is saved as `app.py` in this folder.
3.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install Python Dependencies:**
    ```bash
    pip install Flask flask-cors yfinance pandas pytz
    ```

### Frontend Setup with Vite (Terminal 2)

1.  **Navigate to your main project folder** in a new terminal window.
2.  **Create the Vite Project:** This command creates a new `frontend` folder with a React template.
    ```bash
    npm create vite@latest frontend
    ```
3.  **Navigate into the Frontend Directory:**
    ```bash
    cd frontend
    ```
4.  **Install Dependencies:**
    ```bash
    npm install tailwindcss @tailwindcss/vite
    npm install lucide-react
    ```
5.  update vite.config.ts with
    ```javascript
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
})
    ```
6.  update `src/index.css` to have `@import "tailwindcss";` on the first line
8.  **Update `main.jsx`:** Open `src/main.jsx` and add `import React from 'react'` to the very first line.

---

## 5. Running the Application

1.  **Start the Backend:** In your first terminal (with the Python venv activated), run:
    ```bash
    python app.py
    ```
    The backend server will start on `http://127.0.0.1:5000`. **Keep this terminal running.**

2.  **Start the Frontend:** In your second terminal (inside the `frontend` directory), run:
    ```bash
    npm run dev
    ```
    This will launch the Vite development server. Your browser should open to the local address provided (usually `http://localhost:5173`).

---

## 6. Deployment (Optional)

This application is designed for local use. Deploying it to the web would require additional steps, such as:

* **Backend:** Hosting the Flask application on a cloud service like Heroku, AWS, or Google Cloud Platform, using a production-grade web server like Gunicorn.
* **Frontend:** Building the React app for production (`npm run build`) and serving the static files through a service like Netlify or Vercel.
* **CORS Configuration:** Updating the Flask backend's CORS settings to allow requests from the deployed frontend's domain.
