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
    st.header("📊 Contaduría")

# Formulario para registrar un nuevo gasto o ingreso
with st.expander("Registrar Nuevo Movimiento"):
    with st.form("registro_finanzas"):
        tipo = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
        monto = st.number_input("Monto ($)", min_value=0.0, step=10.0)
        descripcion = st.text_input("Descripción (Ej. Venta de gorra, Pago de luz)")
        guardar = st.form_submit_button("Guardar")
        
        if guardar:
            registrar_movimiento(supabase, tipo, monto, descripcion)
            st.success("Movimiento registrado con éxito")
            st.rerun()

# Mostrar historial y totales
movimientos = obtener_movimientos(supabase)
if movimientos:
    import pandas as pd
    df = pd.DataFrame(movimientos)
    
    # Calcular totales
    total_ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
    total_gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
    ganancia_neta = total_ingresos - total_gastos
    
    # Mostrar métricas en la pantalla
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
    col2.metric("Gastos Totales", f"${total_gastos:,.2f}")
    col3.metric("Ganancia Neta", f"${ganancia_neta:,.2f}")
    
    # Mostrar la tabla con el historial
    st.dataframe(df[['fecha', 'tipo', 'descripcion', 'monto']], use_container_width=True)
