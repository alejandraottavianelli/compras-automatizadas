# 📦 Sistema Automatizado de Compras y Reposición de Stock

Plataforma desarrollada en Python y Streamlit para la gestión, optimización y valorización automática de pedidos de compra a proveedores (Carne Vacuna, Cerdo, Pollo, Pescados y Rebozados).

---

## 🎯 Objetivo del Proyecto

Eliminar la sobrecarga operativa en el armado de pedidos, evitar sobrestock o quiebres de mercadería y garantizar el menor costo financiero seleccionando automáticamente el mejor precio del mercado.

El sistema integra tres pilares clave:
1. **Piso de Seguridad**: Nivel mínimo estático en cámara.
2. **Velocidad de Ventas (Rotación Diaria)**: Cálculo en base al historial del sistema comercial.
3. **Comparativa de Precios con IVA**: Cruce dinámico con las listas de proveedores (Rioplatense, Frimsa, Gorina, Mercedino, Swift, Campo Austral, Soychu / Sede América, Grangys).

---

## 🧮 Lógica de Fórmulas y Algoritmo

* **Venta Diaria Promedio**:
  $$\text{Venta Diaria} = \frac{\text{Ventas del Período}}{\text{Días del Período Evaluado}}$$

* **Stock Objetivo**:
  $$\text{Stock Objetivo} = \max\Big(\text{Piso}, \; \text{Venta Diaria} \times \text{Días Objetivo Cobertura}\Big)$$

* **Pedido Sugerido (Cajas)**:
  $$\text{Pedido Sugerido} = \max\Big(0, \; \text{Stock Objetivo} - (\text{Stock Actual} + \text{Pendiente Ingreso})\Big)$$

---

## 🚀 Estructura de Archivos del Repositorio

* `app.py`: Aplicación principal de Streamlit con interfaz interactiva y visualización de KPIs.
* `homologacion.csv`: Tabla de equivalencias entre los códigos internos de la empresa y la denominación de cada proveedor.
* `requirements.txt`: Librerías de Python requeridas para el despliegue en Streamlit Cloud.

---

## 📖 Instructivo de Uso para el Operador (Sandra)

1. **Ingresar a la App Web**: Acceder a la URL de Streamlit Cloud desde cualquier navegador.
2. **Cargar Parámetros**: Ajustar los días de cobertura objetivo (ej. 15 días) y días del período de ventas.
3. **Cargar Archivos**:
   * Archivo de **Stock Físico** (Excel).
   * Reporte de **Ventas del Período** (Excel exportado del sistema).
4. **Revisión del Tablero**:
   * 🔴 **Riesgo Quiebre**: Cobertura menor a 5 días con venta activa (Prioridad de compra).
   * 🟡 **Reponer**: Stock por debajo del piso o la cobertura deseada.
   * 🟢 **Stock Saludable**: Cobertura suficiente o sobrestock.
5. **Descargar Orden de Compra**: Exportar el archivo CSV/Excel listo con las cantidades y el valorizado final en pesos.
