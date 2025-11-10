import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Order as OrderSchema, AdminLogin

app = FastAPI(title="Sunny Online Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers to convert Mongo docs to JSON safe

def serialize_id(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

@app.get("/")
def read_root():
    return {"message": "Sunny Online Store Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# --- Products ---

@app.post("/api/products", response_model=dict)
async def create_product(product: ProductSchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    product_id = create_document("product", product)
    doc = db["product"].find_one({"_id": ObjectId(product_id)})
    return serialize_id(doc)

@app.get("/api/products", response_model=List[dict])
async def list_products(limit: Optional[int] = 50, category: Optional[str] = None):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    docs = get_documents("product", filter_dict, limit)
    return [serialize_id(d) for d in docs]

# --- Orders ---

@app.post("/api/orders", response_model=dict)
async def create_order(order: OrderSchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    order_id = create_document("order", order)
    doc = db["order"].find_one({"_id": ObjectId(order_id)})
    return serialize_id(doc)

@app.get("/api/orders", response_model=List[dict])
async def list_orders(limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    docs = get_documents("order", {}, limit)
    return [serialize_id(d) for d in docs]

# --- Admin auth (simple password check via env) ---

class AdminAuthResponse(BaseModel):
    success: bool

@app.post("/api/admin/login", response_model=AdminAuthResponse)
async def admin_login(payload: AdminLogin):
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    return AdminAuthResponse(success=(payload.password == admin_password))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
