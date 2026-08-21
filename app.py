import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Gestión de Compras y Reposición", layout="wide")

st.title("📦 Sistema Automatizado de Compras y Valorización")
st.markdown("Cálculo dinámico de pedido sugerido por velocidad de ventas y comparativa automática de precios.")

# --- CARGA DE TABLA DE HOMOLOGACION ---
@st.cache_data
def load_homologacion():
    try:
        df_h = pd.read_csv('homologacion.csv')
        df_h['CODIGO_CLEAN'] = df_h['CODIGO_INTERNO'].astype(str).str.split('.').str[0].str.zfill(7)
        return df_h
    except Exception as e:
        st.error(f"Error al cargar homologacion.csv: {e}")
        return pd.DataFrame()

df_hom = load_homologacion()

# --- SIDEBAR DE CONTROLES ---
st.sidebar.header("⚙️ Parámetros de Compra")
dias_cobertura = st.sidebar.slider("Días Objetivo de Cobertura", min_value=7, max_value=30, value=15)
dias_periodo = st.sidebar.number_input("Días del Período Evaluado en Ventas", min_value=1, value=10)

st.sidebar.header("📁 Carga de Archivos")
file_stock = st.sidebar.file_uploader("1. Archivo de Stock (Excel)", type=["xlsx"])
file_ventas = st.sidebar.file_uploader("2. Reporte de Ventas (Excel)", type=["xlsx"])

# --- PROCESAMIENTO PRINCIPAL ---
if file_stock and file_ventas:
    # 1. Cargar Stock
    df_st = pd.read_excel(file_stock, sheet_name='Grilla_1')
    df_st = df_st.dropna(subset=['Codigo']).copy()
    df_st['CODIGO_CLEAN'] = df_st['Codigo'].astype(str).str.split('.').str[0].str.zfill(7)
    
    # Clean numeric columns in stock
    df_st['PISO'] = pd.to_numeric(df_st['PISO'], errors='coerce').fillna(0)
    df_st['CAJAS STOCK'] = pd.to_numeric(df_st['CAJAS STOCK'].astype(str).str.extract(r'(\d+)')[0], errors='coerce').fillna(0)
    df_st['PENDIENTE DE INGRESO'] = pd.to_numeric(df_st['PENDIENTE DE INGRESO'], errors='coerce').fillna(0)

    # 2. Cargar Ventas
    df_ve = pd.read_excel(file_ventas)
    df_ve['CODIGO_CLEAN'] = df_ve['Cod. producto'].astype(str).str.split('.').str[0].str.zfill(7)
    
    resumen_ve = df_ve.groupby('CODIGO_CLEAN').agg(
        CANTIDAD_VENDIDA=('Cantidad', 'sum')
    ).reset_index()

    # 3. Consolidador de Stock + Ventas + Homologación
    merged = pd.merge(df_st, resumen_ve, on='CODIGO_CLEAN', how='left')
    merged['CANTIDAD_VENDIDA'] = merged['CANTIDAD_VENDIDA'].fillna(0)
    
    final_df = pd.merge(merged, df_hom, on='CODIGO_CLEAN', how='left')

    # 4. Fórmulas de Rotación y Pedido
    final_df['VENTA_DIARIA'] = final_df['CANTIDAD_VENDIDA'] / dias_periodo
    final_df['STOCK_DISPONIBLE'] = final_df['CAJAS STOCK'] + final_df['PENDIENTE DE INGRESO']
    
    # Stock Objetivo = max(Piso, Venta_Diaria * Dias_Cobertura)
    final_df['STOCK_OBJETIVO'] = np.maximum(final_df['PISO'], final_df['VENTA_DIARIA'] * dias_cobertura)
    final_df['SUGERIDO_CAJAS'] = np.maximum(0, np.ceil(final_df['STOCK_OBJETIVO'] - final_df['STOCK_DISPONIBLE']))
    
    final_df['COBERTURA_DIAS'] = np.where(final_df['VENTA_DIARIA'] > 0, final_df['STOCK_DISPONIBLE'] / final_df['VENTA_DIARIA'], 999)

    # Alertas visuales
    def asignar_estado(row):
        if row['COBERTURA_DIAS'] < 5 and row['VENTA_DIARIA'] > 0:
            return "🔴 Riesgo Quiebre"
        elif row['SUGERIDO_CAJAS'] > 0:
            return "🟡 Reponer Piso / Cobertura"
        else:
            return "🟢 Stock Saludable"

    final_df['ESTADO'] = final_df.apply(asignar_estado, axis=1)

    # --- KPI SUMMARY ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ítems Evaluados", len(final_df))
    col2.metric("Total Cajas Sugeridas", int(final_df['SUGERIDO_CAJAS'].sum()))
    col3.metric("Ítems en Riesgo Quiebre", len(final_df[final_df['ESTADO'].str.contains("Riesgo")]))

    # --- TABLA DE RESULTADOS ---
    st.subheader("📋 Tablero de Recomendación de Compras")
    
    cols_display = [
        'CODIGO_CLEAN', 'Descripcion', 'PISO', 'CAJAS STOCK', 
        'PENDIENTE DE INGRESO', 'CANTIDAD_VENDIDA', 'VENTA_DIARIA', 
        'COBERTURA_DIAS', 'SUGERIDO_CAJAS', 'ESTADO'
    ]
    
    st.dataframe(
        final_df[cols_display].rename(columns={
            'CODIGO_CLEAN': 'Código',
            'Descripcion': 'Corte / Producto',
            'CAJAS STOCK': 'Stock Físico',
            'PENDIENTE DE INGRESO': 'Pendientes',
            'CANTIDAD_VENDIDA': f'Ventas ({dias_periodo}d)',
            'VENTA_DIARIA': 'Venta Diaria',
            'COBERTURA_DIAS': 'Días Cobertura',
            'SUGERIDO_CAJAS': 'Pedido Sugerido'
        }),
        use_container_width=True
    )

    # Exportación
    csv_data = final_df[cols_display].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Recomendado en CSV",
        data=csv_data,
        file_name='Recomendacion_de_Compra_Sandra.csv',
        mime='text/csv'
    )
else:
    st.info("💡 Por favor cargá los archivos de Stock y Ventas en la barra lateral izquierda para generar el tablero.")
