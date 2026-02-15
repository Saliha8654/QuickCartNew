QuickCart Backend (Flask + SQLAlchemy + YOLO)
How to run:
1) create venv and install dependencies:
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
2) adjust DATABASE_URL in .env or export DATABASE_URL env var
   (default uses sqlite: sqlite:///quickcart.db)
3) run the app:
   python app.py
API endpoints (prefix /api):
- GET  /products
- POST /products
- GET  /cart
- POST /cart
- PATCH /cart/<id>
- DELETE /cart/<id>
- POST /detect  (multipart/form-data file field 'image')
- POST /weight/verify  (json { weight_g, expected_g, tolerance } )
