import streamlit as st
import pandas as pd
from database import insert_product, get_low_stock, get_available_products, register_sale
from ai_processor import extract_data_from_image

st.set_page_config(page_title="Punto de Venta Automotriz", layout="wide")

DEFAULT_MARGINS = {
    "Iluminacion/Faros": 40.0,
    "Aceites/Aditivos": 25.0,
    "Calaveras": 40.0,
    "Miscelaneos": 35.0
}

def calculate_sale_price(entry_cost, profit_margin):
    cost_with_tax = entry_cost * 1.16
    multiplier = 1 + (profit_margin / 100)
    return cost_with_tax * multiplier

st.title("Sistema de Inventario y Precios")

tab1, tab2, tab3 = st.tabs(["Ingreso de Mercancia", "Punto de Venta", "Dashboard y Alertas"])

with tab1:
    st.header("Registrar Nuevos Productos")
    upload_method = st.radio("Metodo de ingreso:", ["Escaneo con IA (Foto/Factura)", "Registro Manual"])
    
    if upload_method == "Escaneo con IA (Foto/Factura)":
        uploaded_file = st.file_uploader("Sube foto de la mercancia (PNG/JPG/PDF)", type=["png", "jpg", "jpeg", "pdf"])
        
        if uploaded_file is not None:
            with st.spinner("Procesando con IA..."):
                extracted_data = extract_data_from_image(uploaded_file)
            st.success("Datos extraidos correctamente")
            
            col1, col2 = st.columns(2)
            with col1:
                prod_name = st.text_input("Producto", value=extracted_data["name"])
                category = st.selectbox("Categoria", list(DEFAULT_MARGINS.keys()), 
                                        index=list(DEFAULT_MARGINS.keys()).index(extracted_data["category"]) if extracted_data["category"] in DEFAULT_MARGINS else 0)
                cost = st.number_input("Costo Unitario (Sin IVA)", value=float(extracted_data["unit_cost"]))
                
            with col2:
                margin_type = st.radio("Margen de Ganancia", ["Predefinido por Categoria", "Manual"])
                margin = DEFAULT_MARGINS[category] if margin_type == "Predefinido por Categoria" else st.number_input("Porcentaje (%)", value=DEFAULT_MARGINS[category])
                
                final_price = calculate_sale_price(cost, margin)
                st.metric("Precio de Venta (Con IVA y Margen)", f"${final_price:.2f}")
                stock_add = st.number_input("Cantidad entrante", min_value=1, value=1)
                
            if st.button("Guardar en Inventario", type="primary"):
                insert_product(prod_name, cost, category, margin, final_price, stock_add)
                st.toast(f"{prod_name} registrado exitosamente.")
    else:
        st.info("Aqui va el formulario manual (mismos campos sin la extraccion automatica).")

with tab2:
    st.header("Terminal de Punto de Venta")
    
    # 1. Cargar productos disponibles desde la base de datos
    available_products = get_available_products()
    
    if available_products:
        # Convertir a un diccionario para buscar facilmente por ID
        product_dict = {p['id']: p for p in available_products}
        
        # 2. Buscador de productos (Dropdown)
        selected_id = st.selectbox(
            "Buscar articulo para cobrar:",
            options=list(product_dict.keys()),
            format_func=lambda x: f"{product_dict[x]['name']} - ${product_dict[x]['price']:.2f} (Disponibles: {product_dict[x]['stock']})"
        )
        
        if selected_id:
            selected_product = product_dict[selected_id]
            
            col1, col2 = st.columns(2)
            with col1:
                # 3. Selector de cantidad (no te deja vender mas de lo que tienes)
                sell_quantity = st.number_input("Cantidad a vender", min_value=1, max_value=selected_product['stock'], value=1)
            
            with col2:
                # 4. Calculadora del total
                total_to_pay = selected_product['price'] * sell_quantity
                st.metric("Total a Cobrar", f"${total_to_pay:.2f}")
            
            # 5. Boton de cobro
            if st.button("Cobrar y Descontar Inventario", type="primary"):
                register_sale(selected_id, sell_quantity)
                st.success(f"Venta registrada con exito. Se descontaron {sell_quantity} pieza(s).")
                st.rerun() # Refresca la pagina automaticamente para actualizar el stock
    else:
        st.info("Tu inventario esta vacio o todos los productos estan agotados.")

with tab3:
    st.header("Alertas de Stock")
    low_stock = get_low_stock(threshold=5)
    if low_stock:
        df_low = pd.DataFrame(low_stock)
        st.warning(f"Atencion: {len(df_low)} productos requieren reabastecimiento.")
        st.dataframe(df_low[['name', 'category', 'stock']], use_container_width=True)
    else:
        st.success("Inventario en niveles optimos.")