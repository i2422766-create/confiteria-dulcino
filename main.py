
import streamlit as st
from supabase import create_client
from datetime import datetime

# Conexión Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def sb_insert(nombre, precio, categorias, en_venta):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta,
        "ts": datetime.now().isoformat()
    }
    return supabase.table("products").insert(payload).execute()

def sb_listar():
    return supabase.table("products").select("*").order("ts", desc=True).limit(10).execute()

def sb_delete(id_producto):
    return supabase.table("products").delete().eq("id", id_producto).execute()

def main():
    st.title("Confitería Dulcino 🍬")

    menu = ["Registrar producto", "Ver productos", "Eliminar producto"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Registrar producto":
        st.subheader("Agregar nuevo producto")
        nombre = st.text_input("Nombre del producto")
        precio = st.text_input("Precio")
        categorias = st.multiselect("Categorías", ["Snacks", "Bebidas", "Dulces", "Galletas"])
        en_venta = st.checkbox("¿Está en venta?", value=True)

        if st.button("Guardar"):
            if nombre and precio:
                sb_insert(nombre.strip(), float(precio), categorias, en_venta)
                st.success("Producto guardado exitosamente")
            else:
                st.warning("Por favor, completa los campos requeridos")

    elif choice == "Ver productos":
        st.subheader("Productos registrados")
        data = sb_listar()
        productos = data.data

        if productos:
            st.table(productos)
        else:
            st.info("No hay productos registrados.")

    elif choice == "Eliminar producto":
        st.subheader("Eliminar producto")
        data = sb_listar()
        productos = data.data

        if productos:
            opciones = {f"{p['nombre']} – S/ {p['precio']} [{str(p['id'])[:6]}]": p for p in productos}
            seleccion = st.selectbox("Selecciona el producto", list(opciones.keys()))

            if st.button("Eliminar"):
                id_producto = opciones[seleccion]["id"]
                sb_delete(id_producto)
                st.success("Producto eliminado exitosamente")
        else:
            st.info("No hay productos para eliminar.")

if __name__ == "__main__":
    main()
