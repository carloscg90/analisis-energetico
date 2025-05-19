# Dashboard Energético de Colombia y el Mundo

Este proyecto es un Dashboard interactivo desarrollado en **Streamlit** que permite visualizar diferentes análisis energéticos de Colombia y comparativos internacionales.

## 🚀 Funcionalidades

- **Diagnóstico Energético de Colombia**
  - Tendencia Mensual de Energía (2014-2025)
  - Comparativo de Fuentes por Año (2014-2025)
  - Participación de Fuentes en 2024
  - Evolución Histórica de la Diversificación Energética (2014-2025)

- **Análisis Sectorial**
  - Consumo Eléctrico por Sector en Colombia (2022)
  - Evolución del Consumo Energético en Transporte, Residencial e Industrial (2000-2025)

- **Comparativos Internacionales**
  - Participación Renovable en 2024 (Países)
  - Evolución Global de la Participación Renovable (2010-2025)
  - Comparativo Energético Global por Año (2010-2025)

- **Análisis Climático**
  - Evolución y Participación de las Emisiones de CO₂ por Sector en Colombia (2000-2022)

## ⚙️ Instalación Local

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   streamlit run analisis_energetico.py
   ```

## ☁️ Despliegue en Railway

1. Crea un nuevo proyecto en [Railway](https://railway.app).
2. Conecta tu repositorio de GitHub.
3. Configura el Start Command como:
   ```bash
   streamlit run analisis_energetico.py --server.port $PORT --server.address 0.0.0.0
   ```
4. Haz Deploy y obtén tu URL pública.

## 📂 Estructura del Proyecto

```
📦
├── analisis_energetico.py
├── requirements.txt
└── analisis_energetico.db  # Asegúrate de incluir tu base de datos en el repositorio
```

## 📝 Licencia

Este proyecto es de uso privado para análisis energético. Contacta al autor para permisos adicionales.
