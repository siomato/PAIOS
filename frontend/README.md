# PAIOS React Frontend

This is a clean React/Vite replacement for the old HTML/CSS/JS frontend.

## Structure

- `index.html`
- `vite.config.js`
- `package.json`
- `src/main.jsx`
- `src/App.jsx`
- `src/App.css`

## Backend

The frontend expects the PAIOS FastAPI backend at:

`http://127.0.0.1:8000`

The live dashboard uses:

`POST http://127.0.0.1:8000/execute/stream`

## Run

From this frontend folder:

```powershell
npm install
npm run dev
```

Then open:

`http://127.0.0.1:5173`

The existing backend remains unchanged.
