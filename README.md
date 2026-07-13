# 🌿 Aura Vitalis AI Concierge — Sistema de Conserjería Inteligente

¡Bienvenido al repositorio oficial del **AI Concierge de Aura Vitalis Eco-Resort & Spa**! Este sistema transforma la experiencia del huésped mediante un asistente virtual impulsado por Inteligencia Artificial de última generación, diseñado específicamente para operar en entornos hoteleros premium y ecológicos.

La aplicación está construida sobre **Streamlit** para ofrecer una interfaz fluida, y utiliza **LangChain** junto con **Google Gemini 2.5 Flash** para procesar de forma inteligente consultas en lenguaje natural mediante arquitectura RAG (Generación Aumentada por Recuperación).

---

## La app estará disponible en: http://157.137.226.41:8501/#aura-vitalis-eco-resort. La evidencia esta en /assets/auraeco.jpg

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
* **Despliegue:** Servidor Ubuntu (Cloud OCI) / Python 3.12

---

## 🚀 Instrucciones de Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/aura-vitalis-ai.git](https://github.com/tu-usuario/aura-vitalis-ai.git)
   cd aura-vitalis-ai
2. **Instalar dependencias:**
3. **Configurar la API Key:**
4. **Ejecutar la aplicación (Modo Producción):**

---

💬 Ejemplos de Preguntas y Respuestas (Por Perfil)
Perfil 1: Huésped de Relajación (Spa y Bienestar)
Pregunta 1: "¿Qué tipo de terapias ofrecen en el spa?"
Respuesta 1: "Ofrecemos una variedad de terapias holísticas, incluyendo masajes de tejido profundo, aromaterapia con esencias locales y sesiones de hidrotermia. ¿Te gustaría que te muestre un video de nuestras instalaciones?"

Pregunta 2: "Quiero reservar un masaje para el sábado en la tarde."
Respuesta 2: "¡Será un placer consentirte! Para coordinar el horario exacto y el terapeuta, un miembro de nuestro equipo se pondrá en contacto contigo a la brevedad. (El sistema registra el Lead internamente)."

Perfil 2: Huésped Familiar (Alojamiento y Actividades)
Pregunta 1: "¿Qué opciones de habitaciones tienen para una familia de 4 personas?"
Respuesta 1: "Para familias recomendamos nuestra Suite Familiar o dos Habitaciones Deluxe conectadas. Ambas incluyen desayuno orgánico y acceso a las piscinas. Aquí tienes una imagen de la Suite: [Renderiza imagen dinámicamente]"

Pregunta 2: "¿Tienen actividades ecológicas para niños?"
Respuesta 2: "Sí, contamos con senderismo guiado por profesionales, talleres de siembra y observación de aves, ideales para que los más pequeños conecten con la naturaleza."

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

---
