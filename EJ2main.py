# -------------------------------------------------------------
# EJERCICIO – Panel Energético Mensual y Anual
# Autor: Héctor Fernández-Clemente Cicuéndez
# -------------------------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN INICIAL
# ---------------------------------------------------------

st.set_page_config(page_title="Inventario TechZone")
st.title("Sistema de Gestión y Análisis Inteligente de Inventario – TechZone")

archivo = "InventarioTechZone.xlsx"

# =========================================================
# PREGUNTA 1 – CARGA DEL ARCHIVO
# =========================================================

st.header("Carga del archivo")

try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error(f"No se encontró el archivo {archivo}")
    st.stop()
except Exception:
    st.error("Error inesperado al cargar el archivo.")
    st.stop()
else:
    st.success("Archivo cargado correctamente.")

# =========================================================
# PREGUNTA 2 – CONVERSIÓN DE FECHA Y TABLA
# =========================================================

st.header("Conversión de fecha y visualización")

df["FechaIngreso"] = pd.to_datetime(df["FechaIngreso"])
st.dataframe(df)

# =========================================================
# PREGUNTA 3 – FILTRO POR CATEGORÍA
# =========================================================

st.header("Filtro por categoría")

categorias = df["Categoria"].unique()
filtro_cat = st.multiselect("Selecciona categoría(s):", categorias, default=categorias)
df_filtrado = df[df["Categoria"].isin(filtro_cat)]

# =========================================================
# PREGUNTA 4 – FILTRO POR ESTADO
# =========================================================

st.header("Filtro por estado del producto")

estados = ["Disponible", "Agotado", "Descontinuado", "Crítico"]
filtro_estado = st.multiselect("Selecciona estado(s):", estados, default=estados)
df_filtrado = df_filtrado[df_filtrado["Estado"].isin(filtro_estado)]

# =========================================================
# PREGUNTA 5 – FILTRO POR RANGO DE PRECIOS
# =========================================================

st.header("Filtro por rango de precios")

min_p, max_p = int(df["Precio"].min()), int(df["Precio"].max())
rango = st.slider("Rango de precios:", min_p, max_p, (min_p, max_p))
df_filtrado = df_filtrado[(df_filtrado["Precio"] >= rango[0]) & (df_filtrado["Precio"] <= rango[1])]

# =========================================================
# PREGUNTA 6 – BÚSQUEDA POR NOMBRE O PALABRA CLAVE
# =========================================================

st.header("Búsqueda por nombre o palabra clave")

busqueda = st.text_input("Buscar producto:")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado["Producto"].str.contains(busqueda, case=False)]

# =========================================================
# PREGUNTA 7 – FILTRO POR STOCK MÍNIMO
# =========================================================

st.header("Filtro por stock mínimo")

if st.checkbox("Mostrar solo productos con stock mínimo (< 10)"):
    df_filtrado = df_filtrado[df_filtrado["Stock"] < 10]

st.write("### Inventario filtrado")
st.dataframe(df_filtrado)

# =========================================================
# PREGUNTA 8 – FORMULARIO DE REGISTRO DE PRODUCTOS
# =========================================================

st.header("Registro de nuevos productos")

def generar_codigo():
    ahora = datetime.now()
    return f"PR-{ahora.strftime('%y%m%d-%H%M%S')}"

with st.form("form_registro"):
    st.write("### Formulario de registro")

    nombre = st.text_input("Nombre del producto")
    categoria = st.selectbox("Categoría", categorias)
    precio = st.number_input("Precio unitario", min_value=0.0)
    stock = st.number_input("Stock disponible", min_value=0)
    fecha_ingreso = st.date_input("Fecha de ingreso")

    estado_manual = st.checkbox("Marcar como descontinuado")

    enviado = st.form_submit_button("Registrar")

    if enviado:
        errores = []

        if nombre.strip() == "":
            errores.append("El nombre no puede estar vacío.")
        if precio <= 0:
            errores.append("El precio debe ser mayor que 0.")
        if fecha_ingreso > datetime.now().date():
            errores.append("La fecha no puede ser futura.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            codigo = generar_codigo()

            if estado_manual:
                estado = "Descontinuado"

# =========================================================
# PREGUNTA 9 – DETERMINACION AUTOMATICA DEL ESTADO
# =========================================================
            else:
                if stock == 0:
                    estado = "Agotado"
                elif stock < 5:
                    estado = "Crítico"
                else:
                    estado = "Disponible"

            nuevo = {
                "Codigo": codigo,
                "Producto": nombre,
                "Categoria": categoria,
                "Precio": precio,
                "Stock": stock,
                "FechaIngreso": fecha_ingreso,
                "Estado": estado
            }

            st.success("Producto registrado correctamente.")
            st.write(nuevo)

# =========================================================
# PREGUNTA 10 – CÁLCULOS Y MÉTRICAS
# =========================================================

st.header("– Cálculos y métricas avanzadas")

df_filtrado["ValorTotal"] = df_filtrado["Precio"] * df_filtrado["Stock"]
df_filtrado["MargenGanancia"] = df_filtrado["Precio"] * 0.12
df_filtrado["DiasEnInventario"] = (datetime.now() - df_filtrado["FechaIngreso"]).dt.days

st.write("### Tabla con métricas avanzadas")
st.dataframe(df_filtrado)

# =========================================================
# PREGUNTA 11 – GRÁFICOS
# =========================================================

st.header("Gráficos")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))

# Cantidad por categoría
df_cat = df_filtrado["Categoria"].value_counts()
ax1.bar(df_cat.index, df_cat.values)
ax1.set_title("Cantidad por categoría")
ax1.set_xticklabels(df_cat.index, rotation=45)

# Valor total por categoría
df_valor = df_filtrado.groupby("Categoria")["ValorTotal"].sum()
ax2.pie(df_valor, labels=df_valor.index, autopct="%1.1f%%")
ax2.set_title("Valor total por categoría")

st.pyplot(fig)

# TOP 5 productos más valiosos
st.write("### TOP 5 productos más valiosos")

df_top = df_filtrado.sort_values("ValorTotal", ascending=False).head(5)

fig2, ax3 = plt.subplots()
ax3.bar(df_top["Producto"], df_top["ValorTotal"])
ax3.set_title("TOP 5 productos más valiosos")
plt.xticks(rotation=45)

st.pyplot(fig2)
