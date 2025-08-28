
import streamlit as st
from supabase import create_client
from datetime import datetime

# Conexión a Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Insertar producto
def sb_insert(nombre, precio, categorias, en_venta):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta,
        "ts": datetime.now().isoformat()
    }
    data = supabase.table("products").insert(payload).execute()
    return data

# Obtener productos
def sb_get():
    data = supabase.table("products").select("*").execute()
    return data.data

# Eliminar producto por ID
def sb_delete(product_id):
    supabase.table("products").delete().eq("id", product_id).execute()

# Página principal
def main():
    st.title("Confitería Dulcino 🍬")

    st.header("Registrar producto nuevo")
    with st.form("product_form"):
        nombre = st.text_input("Nombre del producto")
        precio = st.number_input("Precio (S/)", min_value=0.0, step=0.5)
        categorias = st.text_input("Categoría")
        en_venta = st.checkbox("¿Disponible para la venta?")
        submitted = st.form_submit_button("Guardar")

        if submitted:
            sb_insert(nombre.strip(), float(precio), categorias, en_venta)
            st.success(f"Producto '{nombre}' guardado exitosamente.")

    st.header("Productos registrados")
    productos = sb_get()

    if productos:
        st.table(productos)

        st.header("Eliminar producto")
        opciones = {
            f"{p['nombre']} – S/ {p['precio']} [{str(p['id'])[:6}]}": p
            for p in productos
        }
        seleccion = st.selectbox("Selecciona un producto para eliminar", opciones.keys())
        if st.button("Eliminar"):
            producto = opciones[seleccion]
            sb_delete(producto["id"])
            st.warning(f"Producto '{producto['nombre']}' eliminado.")
            st.experimental_rerun()
    else:
        st.info("No hay productos registrados.")

if __name__ == "__main__":
    main()
