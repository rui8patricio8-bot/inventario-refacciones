from supabase import create_client, Client

SUPABASE_URL = "https://qdmjiascmnuenpsrffyz.supabase.co"
SUPABASE_KEY = "sb_publishable_eh28vWgMAjqNqj8vgZvU4g_TePha4Jo"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Conexion exitosa a Supabase.")
except Exception as e:
    print(f"Error al conectar con Supabase: {e}")

def insert_product(name, cost, category, margin, final_price, stock):
    data = {
        "name": name, "cost": cost, "category": category, 
        "margin": margin, "price": final_price, "stock": stock
    }
    return supabase.table("products").insert(data).execute()

def get_low_stock(threshold=5):
    response = supabase.table("products").select("*").lte("stock", threshold).execute()
    return response.data

def get_available_products():
    """Obtiene todos los productos que tienen al menos 1 pieza en stock."""
    response = supabase.table("products").select("*").gt("stock", 0).order("name").execute()
    return response.data

def register_sale(product_id, quantity_sold):
    product = supabase.table("products").select("stock").eq("id", product_id).single().execute()
    if product.data:
        new_stock = product.data['stock'] - quantity_sold
        return supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()
    return None