import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Cargar claves desde el entorno seguro
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ALLOWED_CATEGORIES = ["Chocolate", "Galletas", "Caramelos", "Snacks"]

def sb_list():
    res = supabase.table("products").select("*").order("ts", desc=True).execute()
    return res.data

def sb_insert(nombre, precio, categorias, en_venta):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta,
        "ts": datetime.utcnow().isoformat()
    }
    supabase.table("products").insert(payload).execute()

def sb_update(id_, nombre, precio, categorias, en_venta):
    payload = {
        "nombre": nombre,
        "precio": precio,
        "categorias": categorias,
        "en_venta": en_venta
    }
    supabase.table("products").update(payload).eq("id", id_).execute()

def sb_delete(id_):
    supabase.table("products").delete().eq("id", id_).execute()

def validar(nombre, precio, categorias):
    if not nombre or len(nombre.strip()) == 0 or len(nombre.strip()) > 20:
        return "El nombre es obligatorio y debe tener menos de 20 caracteres."
    try:
        precio = float(precio)
        if precio <= 0 or precio > 999:
            return "El precio debe ser mayor a 0 y menor a 999."
    except ValueError:
        return "El precio debe ser un número válido."
    if not categorias or not all(c in ALLOWED_CATEGORIES for c in categorias):
        return "Debes seleccionar al menos una categoría válida."
    return None

def mostrar_productos():
    data = sb_list()
    if not data:
        st.info("No hay productos registrados.")
        return []
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    return data

def main():
    st.title("Confitería Dulcino - Registro de productos")

    st.subheader("Agregar nuevo producto")
    with st.form("formulario_agregar"):
        nombre = st.text_input("Nombre del producto")
        precio = st.text_input("Precio")
        categorias = st.multiselect("Categorías", ALLOWED_CATEGORIES)
        en_venta = st.radio("¿Está en venta?", [True, False], format_func=lambda x: "Sí" if x else "No")
        submitted = st.form_submit_button("Guardar")

        if submitted:
            error = validar(nombre, precio, categorias)
            if error:
                st.warning(error)
            else:
                sb_insert(nombre.strip(), float(precio), categorias, en_venta)
                st.success("Producto agregado exitosamente")

    st.subheader("Productos registrados")
    productos = mostrar_productos()

    if productos:
        opciones = {f"{p['nombre']} - S/ {p['precio']} [{p['id'][:6]}]": p for p in productos}
        seleccion = st.selectbox("Selecciona un producto para editar/eliminar", list(opciones.keys()))
        producto_sel = opciones[seleccion]

        st.write("### Editar producto")
        with st.form("formulario_editar"):
            nombre_e = st.text_input("Nombre", value=producto_sel['nombre'])
            precio_e = st.text_input("Precio", value=str(producto_sel['precio']))
            categorias_e = st.multiselect("Categorías", ALLOWED_CATEGORIES, default=producto_sel['categorias'])
            en_venta_e = st.radio("¿Está en venta?", [True, False], index=0 if producto_sel['en_venta'] else 1,
                                   format_func=lambda x: "Sí" if x else "No")
            col1, col2 = st.columns(2)
            editar = col1.form_submit_button("Actualizar")
            eliminar = col2.form_submit_button("Eliminar")

            if editar:
                error = validar(nombre_e, precio_e, categorias_e)
                if error:
                    st.warning(error)
                else:
                    sb_update(producto_sel['id'], nombre_e.strip(), float(precio_e), categorias_e, en_venta_e)
                    st.success("Producto actualizado correctamente")

            if eliminar:
                sb_delete(producto_sel['id'])
                st.success("Producto eliminado correctamente")

if __name__ == '__main__':
    main()