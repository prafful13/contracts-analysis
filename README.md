# Options Income Screener Application

## 1. Project Overview

The Options Income Screener is a web-based tool designed for options traders who focus on income-generating strategies like selling cash-secured puts and covered calls. It provides a user-friendly interface to scan the market for potentially profitable contracts based on a variety of customizable criteria.

The application fetches real-time (or last-close) market data and presents the best opportunities in sortable tables, allowing traders to quickly identify contracts that match their specific risk tolerance and return objectives.

---

## 2. Architecture

This application is built on a modern client-server architecture, separating the user interface from the data processing logic. The project is organized into two main top-level directories: `frontend` and `backend`.

* **Backend (Python & Flask):** A lightweight Python server built with the Flask framework, located in the `backend` directory. Its sole responsibility is to handle the heavy lifting:
    * Receiving analysis requests from the frontend.
    * Using the `yfinance` library to fetch real options data from Yahoo Finance.
    * Filtering and analyzing thousands of contracts based on the user's criteria.
    * Sending the processed data back to the frontend as a clean JSON response.

* **Frontend (React.js & Vite):** A fast, modern single-page application (SPA) built with React and Vite, located in the `frontend` directory. Its responsibilities are:
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

To run the application locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    *   **Python:** Install the required Python packages from `requirements.txt`. The `-e .` flag installs the backend code as an editable package.
        ```bash
        pip install -r requirements.txt
        pip install -e .
        
        pip install '.[test]'
        ```
    *   **Frontend:** Install the Node.js packages for the frontend.
        ```bash
        cd frontend
        npm install
        cd ..
        ```

---

## 5. Running the Application

This project includes a convenience script to start both the backend and frontend servers concurrently.

**From the root of the project, run:**
```bash
./start.sh
```

This will:
* Start the Python backend server.
* Start the React frontend development server.
* You can view the application at `http://localhost:5173`.

To stop the application, you can use the `stop.sh` script:
```bash
./stop.sh
```

---

## 6. Running Tests

This project uses `pytest` for testing the backend. To run the tests, make sure you have installed the development dependencies and the package in editable mode (as described in the setup section).

**From the root of the project, run:**
```bash
pytest backend/tests
```

This will automatically discover and run the tests in the `backend/tests/` directory.

---

## 7. Deployment (Optional)

This application is designed for local use. Deploying it to the web would require additional steps, such as:

* **Backend:** Hosting the Flask application on a cloud service like Heroku, AWS, or Google Cloud Platform, using a production-grade web server like Gunicorn.
* **Frontend:** Building the React app for production (`npm run build`) and serving the static files through a service like Netlify or Vercel.
* **CORS Configuration:** Updating the Flask backend's CORS settings to allow requests from the deployed frontend's domain.
