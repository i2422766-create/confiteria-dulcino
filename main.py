
import os
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import List
from dataclasses import dataclass

# ---------------------------
# CONFIGURACIÓN
# ---------------------------

ALLOWED_CATEGORIES = [
    "Chocolates", "Caramelos", "Mashmelos",
    "Galletas", "Salados", "Gomas de mascar"
]

CSV_DIR = "datos_sinteticos"
CSV_PATH = os.path.join(CSV_DIR, "products.csv")


# ---------------------------
# CLASES PERSONALIZADAS
# ---------------------------

class ValidationError(Exception):
    pass

class PriceParseError(ValidationError):
    pass


# ---------------------------
# DATACLASS PARA PRODUCTO
# ---------------------------

@dataclass
class Producto:
    nombre: str
    precio: float
    categorias: List[str]
    en_venta: bool
    ts: str


# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------

def ensure_dir():
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

def load_df():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        return pd.DataFrame(columns=["nombre", "precio", "categorias", "en_venta", "ts"])

def validate(nombre, precio, categorias, en_venta_label):
    # Validar nombre
    if not nombre:
        raise ValidationError("El nombre no puede estar vacío.")
    if len(nombre) > 20:
        raise ValidationError("El nombre no puede tener más de 20 caracteres.")

    # Validar precio
    try:
        precio = float(precio)
    except ValueError:
        raise PriceParseError("Por favor verifique el campo del precio.")

    if precio <= 0 or precio >= 999:
        raise ValidationError("El precio debe ser mayor a 0 y menor a 999.")

    # Validar categorías
    if not categorias:
        raise ValidationError("Debe seleccionar al menos una categoría.")
    for cat in categorias:
        if cat not in ALLOWED_CATEGORIES:
            raise ValidationError(f"Categoría inválida: {cat}")

    # Validar en_venta (Sí/No)
    if en_venta_label not in ["Sí", "No"]:
        raise ValidationError("Seleccione si el producto está en venta o no.")

    en_venta = en_venta_label == "Sí"

    return nombre, precio, categorias, en_venta


# ---------------------------
# INTERFAZ STREAMLIT
# ---------------------------

st.set_page_config(page_title="Confitería Dulcino", layout="centered")
st.title("🍬 Registro de productos - Confitería Dulcino")

st.markdown("Complete el siguiente formulario para agregar un nuevo producto:")

with st.form("form-producto"):
    col1, col2 = st.columns([2, 1])

    with col1:
        nombre = st.text_input("Nombre del producto", max_chars=20)
        precio = st.text_input("Precio del producto")

    with col2:
        categorias = st.multiselect("Categorías", options=ALLOWED_CATEGORIES)
        en_venta_label = st.radio("¿Está en venta?", options=["Sí", "No"])

    submitted = st.form_submit_button("Guardar")

    if submitted:
        try:
            # Validación
            nombre_val, precio_val, categorias_val, en_venta_val = validate(
                nombre, precio, categorias, en_venta_label
            )

            # Crear producto
            nuevo_producto = {
                "nombre": nombre_val,
                "precio": precio_val,
                "categorias": ";".join(categorias_val),
                "en_venta": en_venta_val,
                "ts": datetime.now().isoformat()
            }

            # Guardar en CSV
            df = load_df()
            df = pd.concat([df, pd.DataFrame([nuevo_producto])], ignore_index=True)
            ensure_dir()
            df.to_csv(CSV_PATH, index=False, encoding="utf-8")

            st.success("✅ ¡Felicidades, su producto se agregó!")

        except PriceParseError as ppe:
            st.error("⚠️ Por favor verifique el campo del precio.")
        except ValidationError as ve:
            st.error("❌ Lo sentimos, no pudo crear este producto.")
            st.warning(f"Detalle: {str(ve)}")
        except Exception as e:
            st.error("❌ Error inesperado. Contacte al soporte.")
            st.warning(f"Debug: {str(e)}")
