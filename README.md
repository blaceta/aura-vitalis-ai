# 🌿 Aura Vitalis AI Concierge — Sistema de Conserjería Inteligente

¡Bienvenido al repositorio oficial del **AI Concierge de Aura Vitalis Eco-Resort & Spa**! Este sistema transforma la experiencia del huésped mediante un asistente virtual impulsado por Inteligencia Artificial de última generación, diseñado específicamente para operar en entornos hoteleros premium y ecológicos.

La aplicación está construida sobre **Streamlit** para ofrecer una interfaz fluida, y utiliza **LangChain** junto con **Google Gemini 2.5 Flash** para procesar de forma inteligente consultas en lenguaje natural mediante arquitectura RAG (Generación Aumentada por Recuperación).

---

## ✨ Características Principales

El sistema ha sido refinado exhaustivamente para ofrecer estabilidad de nivel industrial y una experiencia de usuario (UX) impecable:

* **🧠 Memoria Cognitiva Conversacional:** Supera la amnesia nativa de los LLM mediante un puente inteligente que inyecta el historial reciente de la conversación en cada consulta, permitiendo interacciones humanas fluidas.
* **🖼️ Interceptores Gráficos en Tiempo Real:** El motor analiza la respuesta de la IA antes de mostrarla. Si el huésped consulta por habitaciones, el sistema intercepta etiquetas ocultas para renderizar dinámicamente imágenes locales (`assets/`) de alta calidad.
* **📊 Captación de Leads Automatizada:** Cuenta con lógica nativa para detectar intenciones comerciales (`[REGISTRAR_LEAD:]`), limpiando el texto visual para el usuario mientras procesa la información en segundo plano.
* **🛡️ Blindaje contra Fallos de API:** Estructura protegida mediante bloques `try/except`. El sistema captura elegantemente errores de saturación de servidores de Google (Error 503) o límites de cuota (Error 429), respondiendo de forma cortés en lugar de colapsar.
* **🎨 Interfaz de Marca Blanca Premium:** Diseño visual estilizado mediante inyección de CSS. Oculta menús nativos y adopta la paleta corporativa: fondo central verde menta ecológico (`#F0F7F4`) con una barra lateral en verde bosque profundo (`#1E3F2D`) de alto contraste.
* **🎥 Galería Multimedia Interactiva:** Incorpora paneles dinámicos en pestañas (`st.tabs`) para reproducir de forma local videos de presentación del hotel, el spa y las habitaciones sin sobrecargar la pantalla inicial.

---

## 🛠️ Stack Tecnológico

* **Frontend:** Streamlit (Componentes nativos de chat, selectores y multimedia).
* **Orquestación IA:** LangChain (Cadenas de recuperación estructuradas).
* **Modelo de Lenguaje:** Google Gemini 2.5 Flash.
* **Base de Conocimiento:** VectorStore ChromaDB (Persistencia de datos del resort).
* **Entorno:** Python 3.12 desplegado en Servidor Cloud Ubuntu.

---

## 📂 Estructura del Proyecto

```text
aura-vitalis-ai/
│
├── assets/                 # Recursos multimedia locales (Fotos y Videos)
├── chroma_db/              # Base de datos vectorial persistente (Ignorada en Git)
├── app.py                  # Aplicación principal y lógica de chat
├── ingest.py               # Script de indexación de documentos a ChromaDB
├── requirements.txt        # Dependencias de Python
├── .gitignore              # Filtro protector de archivos (Oculta BD y logs)
└── README.md               # Documentación del proyecto
