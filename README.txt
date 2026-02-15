# QuickCart Week 1–2 Starter

This folder contains:
- **quickcart-backend**: Flask + SQLAlchemy + SQLite (switchable to PostgreSQL)
- **quickcart-frontend-src**: `/src` and `/public` to drop into a Create React App project

## How to Run (Step-by-step)

### 1) Backend
```
cd quickcart-backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Backend runs at http://localhost:5000

> To use PostgreSQL later, set `DATABASE_URL` env var, e.g.
> `set DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/quickcart`

### 2) Frontend
Create a CRA app first (empty):
```
npx create-react-app quickcart-frontend
cd quickcart-frontend
npm install axios react-router-dom
```
Now copy **the contents** of this folder's `quickcart-frontend-src/src` into your CRA `/src`,
and copy `quickcart-frontend-src/public` into your CRA `/public` (overwrite).

Finally, run:
```
npm start
```
Frontend runs at http://localhost:3000

### 3) Test
- Search for items like "Dawn" or "Butter"
- Add to bag -> See Cart Summary and totals
