import os
import csv
from datetime import datetime
import google.generativeai as genai
import streamlit as st
import requests
import re

# Componentes de Orquestación de IA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
load_dotenv()

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="Concierge Aura Vitalis", page_icon="🤖", layout="centered")
st.markdown("""
<style>
/* Ocultar elementos por defecto */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
headder {visibility: hidden;}
/* 1. Area principal (Chat y contenido) - Color claro */
.stApp {
    background-color: #F0F7F4; /* Verde suave*/
}
/* Texto oscuroen area pincipal */
.stApp, .stApp p. .stApp h1, .stApp h2, .stApp h3, .stApp span {
    color: #1A1A1A !important;
}
/* 2. Barra lateral (selector de visitante) - color oscuro */
[data-testid="stSidebar"] {
    background-color: #1E3F2D; /* verde profundo */
}
/* 3. Asegurar que los textos en la barra sean legibles */
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Aura Vitalis Eco - Resort")
st.caption("Tu Concierge de Bienestar 24/7. En que te puedo consentir hoy?")
st.image("assets/fachada.png", use_container_width=True)

st.markdown("### Descubre Aura Vitalis")
tab1, tab2, tab3 = st.tabs(["Exterior", "Yoga", "Piscina"])
with tab1:
    st.video("assets/recorrido.mp4")
with tab2:
    st.video("assets/yoga.mp4")
with tab3:
    st.video("assets/piscina.mp4")

st.divider()

# Mantener la base de datos vectorial en la caché de Streamlit para que no se recargue en cada clic
@st.cache_resource
def inicializar_motor_rag():
    ruta_manual = "data/manual_hotel.txt"
    if not os.path.exists(ruta_manual):
        return None
        
    with open(ruta_manual, "r", encoding="utf-8") as f:
        documento_texto = f.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = text_splitter.create_documents([documento_texto])

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma.from_documents(chunks, embeddings)
    return vector_store.as_retriever(search_kwargs={"k": 3})

retriever = inicializar_motor_rag()

# ==========================================
# 2. SISTEMA DE PERSISTENCIA (CSV LOGS)
# ==========================================
def registrar_evento_sistema(archivo_nombre, encabezados, datos_fila):
    ruta_carpeta = "data"
    os.makedirs(ruta_carpeta, exist_ok=True)
    ruta_archivo = os.path.join(ruta_carpeta, archivo_nombre)
    archivo_nuevo = not os.path.exists(ruta_archivo)
    with open(ruta_archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if archivo_nuevo:
            writer.writerow(encabezados)
        writer.writerow(datos_fila)

# ==========================================
# 3. INTERFAZ GRÁFICA (STREAMLIT UI)
# ==========================================
st.title("🌿 Aura Vitalis Eco-Resort")
st.subheader("Concierge Virtual de Bienestar")

# Selector de Perfil en la barra lateral
with st.sidebar:
    st.header("Configuración de Entorno")
    entorno = st.radio(
        "Seleccione su estado actual:",
        ("Cliente Potencial (Web)", "Huésped en Estadía (Habitación)")
    )
    st.divider()
    st.caption("Desarrollado con Ecosistema RAG y OCI.")

if retriever is None:
    st.error("❌ Archivo 'data/manual_hotel.txt' no encontrado. Por favor verifique sus carpetas.")
else:
    # Configurar las reglas dinámicas del prompt según la barra lateral
    if entorno == "Huésped en Estadía (Habitación)":
        perfil_usuario = "HÚESPED ACTUAL EN ESTADÍA INTERNA."
        regla_multimedia = "PROHIBIDO mostrar el video promocional general ([MOSTRAR_VIDEO]). Concéntrate en soporte logístico y solución de quejas."
    else:
        perfil_usuario = "CLIENTE POTENCIAL INTERESADO DESDE CANAL DIGITAL."
        regla_multimedia = """PASO 1 (Solo texto): Si el usuario pregunta "tipos de habitaciones tienen" o piden informacion de las mismas , DEBES limitarte a describir las habitaciones y sus caracteristicas basandote en los documentos. Al final de tu explicacion, invitalo preguntando: te gustaria ver una fotografia de nuestra habitacion". Esta estrictamente prohibido incluir la etiqueta de imagen en este paso!
                           Paso 2 (Mostrar imagen): SOLO SI el usuario pide rxplicitamente "ver", "mostrar foto", o dice "si" del Paso 1. DEBES incluir al final de tu respuesta esta etiqueta exacta [MOSTRAR_IMAGEN: assets/nombre_exacto_de_tu_foto.pgn]
                           """

    # Inicializar el historial de chat en la sesión si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "¡Hola! Soy su Concierge de Bienestar en Aura Vitalis. ¿En qué puedo asistirle hoy para armonizar su experiencia?"}]
    if "bloqueado" not in st.session_state:
        st.session_state.bloqueado = False

    # Mostrar mensajes previos del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Si el canal fue cedido a un humano, bloquear nuevas entradas de texto
    if st.session_state.bloqueado:
        st.info("📨 [SISTEMA]: Su consulta ha sido transferida a un asesor humano. La IA se encuentra inactiva.")
    else:
        # Entrada de texto del usuario
        if prompt_usuario := st.chat_input("Escriba su pregunta aquí..."):
            # Mostrar pregunta del usuario
            with st.chat_message("user"):
                st.markdown(prompt_usuario)
                st.session_state.messages.append({"role": "user", "content": prompt_usuario})
            if "messages" in st.session_state and len(st.session_state.messages):
                ultimo_mensaje_bot = st.session_state.messages[-2]["content"]
                historial_reciente = f"Contexto previo de la conversacion: tu preguntaste esto: '{ultimo_mensaje_bot}'."
            prompt_enriquecida = f"{historial_reciente} Ahora el usuario responde: '{prompt_usuario}'. Aplica las reglas y continua el proceso."

            def guardar_datos_csv(texto_respuesta):
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Buscar y guardar Leads
                match_lead = re.search(r'\[REGISTRAR_LEAD:(.*?)\]', texto_respuesta, re.IGNORECASE)
                if match_lead:
                    datos = match_lead.group(1).strip()
                    archivo = 'clientes_potenciales.csv'
       	            if not os.path.exists(archivo):
                        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                            csv.writer(f).writerow(['Fecha_Hora', 'Datos_Prospecto'])
                    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                       csv.writer(f).writerow([fecha_actual, datos])
                    texto_respuesta = re.sub(r'\[REGISTRAR_LEAD:.*?\]', '', texto_respuesta, flags=re.IGNORECASE)

    # 2. Buscar y guardar Mantenimiento
                match_maint = re.search(r'\[ALERTA_MANTENIMIENTO:(.*?)\]', texto_respuesta, re.IGNORECASE)
                if match_maint:
                    datos = match_maint.group(1).strip()
                    archivo = 'reportes_mantenimiento.csv'
                    if not os.path.exists(archivo):
                        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                            csv.writer(f).writerow(['Fecha_Hora', 'Reporte_Habitacion'])
                    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow([fecha_actual, datos])
                    texto_respuesta = re.sub(r'\[ALERTA_MANTENIMIENTO:.*?\]', '', texto_respuesta, flags=re.IGNORECASE)

    # 3. Buscar y guardar Check-in
                match_checkin = re.search(r'\[REGISTRAR_CHECKIN:(.*?)\]', texto_respuesta, re.IGNORECASE)
                if match_checkin:
                    datos = match_checkin.group(1).strip()
                    archivo = 'registros_checkin.csv'
                    if not os.path.exists(archivo):
                        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                            csv.writer(f).writerow(['Fecha_Hora_Registro', 'Datos_Llegada'])
                    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow([fecha_actual, datos])
                    texto_respuesta = re.sub(r'\[REGISTRAR_CHECKIN:.*?\]', '', texto_respuesta, flags=re.IGNORECASE)

    # 4. Buscar y guardar Check-out
                match_checkout = re.search(r'\[ALERTA_CHECKOUT:(.*?)\]', texto_respuesta, re.IGNORECASE)
                if match_checkout:
                    datos = match_checkout.group(1).strip()
                    archivo = 'alertas_checkout.csv'
                    if not os.path.exists(archivo):
                        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                            csv.writer(f).writerow(['Fecha_Hora_Salida', 'Habitacion'])
                    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow([fecha_actual, datos])
                    texto_respuesta = re.sub(r'\[ALERTA_CHECKOUT:.*?\]', '', texto_respuesta, flags=re.IGNORECASE)

                return texto_respuesta.strip()
            # Construir e invocar la cadena de IA
            class NativeGeminiChat(Runnable):
                def invoke(self, inputs, config=None, **kwargs):
                    url = (f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={os.getenv('GOOGLE_API_KEY')}")
                    if hasattr(inputs, "to_string"):
                        prompt_final = inputs.to_string()
                    elif isinstance(inputs, dict):
                        prompt_final = inputs.get("input", str(inputs))
                    else:
                        prompt_final = str(inputs)

                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt_final}]
                        }],
                        "generationConfig": {
                            "temperature": 0.1
                        }
                    }

                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        res_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                        # --- NUEVA LÍNEA: Interceptar datos y limpiar texto ---
                        res_text = guardar_datos_csv(res_text)
                        return AIMessage(content=res_text)
                    else:
                        raise Exception(f"Error en Gemini API: {response.text}")
            llm = NativeGeminiChat()

            system_prompt = """
                Eres el Concierge de Bienestar de 'Aura Vitalis Eco-Resort & Spa'.
                El usuario interactuando es un: {perfil_usuario}
                Regla de Control de Medios: {regla_multimedia}
                JERARQUÍA:
                1. Si preguntan datos del manual (horarios, políticas, wifi), responde directo sin pedir datos ni etiquetas.
                2. INDECISIÓN COMERCIAL: Si duda en reservar, pide NOMBRE y CONTACTO. Al final agrega: '[REGISTRAR_LEAD: Motivo]'.
                3. RECLAMOS: Si está molesto, discúlpate empáticamente y agrega al final: '[ALERTA_QUEJA: Detalles]'.
                4. Contexto:{context}"
                5. CHECK-IN DIGITAL: Si un usuario con reserva confirmada desea hacer check-in, pídele su nombre completo y hora estimada de llegada. Finaliza diciendo: 'Su pre-registro está listo, lo esperamos con una bebida de bienvenida.' y agrega: '[REGISTRAR_CHECKIN: Nombre - Hora LLegada]'.
                6. CHECK-OUT EXPRESS: Si un huésped desea entregar la habitación, pídele su número de habitación. Finaliza diciendo: 'Hemos procesado su salida. El personal de botones va por su equipaje. ¡Buen viaje!' y agrega: '[ALERTA_CHECKOUT: Habitación]'.
                7. CIERRE DE CONVERSACION: Si el usuario se despide, dice 'gracias' sin hacer otra pregunta, o indica claramente que ya no necesita mas asistencia , despidete de manera formal, cortes y muy breve. TIENES PROHIBIDO hacer preguntas adiconales o dejar la conversacion abierta (ej. no digas 'hay algo mas en lo que te pueda ayudar?'). Simplemente despidete y cierra el ciclo.
                8. IMAGENES DE HABITACIONES: Si te preguntan por un tipo de habitacion o por las instalaciones del eco - resort , debes incluir en tu respuesta, justo antes de empezar la descripcion, la siguiente etiqueta exacta: '[MOSTRAR_IMAGEN:assets/nombre_de_la_imagen.png]', reemplazando 'nombre_de_la_imagen.png' con el nombre correcto de la foto en la carpeta 'assets' para esa area. No muestres la etiqueta al usuario, yo la interceptare.
                 **Ejemplos de etiquetas de imagen que debes usar:**
                 * Para la habitacion Ocean_Wellness_villa: '[MOSTRAR_IMAGEN: assets/Ocean_Wellness_Villa.png]'
                 * Para la habitacion Canopy_bungalow: '[MOSTRAR_IMAGEN: assets/canopy_bungalow.png]'
                 * Para la piscina agua viva: '[MOSTRAR_IMAGEN: assets/agua_viva.png]'
            """

            prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
            rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt_template))

            # --- PROCESAR INTERCEPTORES EN LA INTERFAZ GRÁFICA ---
            with st.chat_message("assistant"):
                try:
                    response = rag_chain.invoke(
                        {"input": prompt_enriquecida,
                        "perfil_usuario": perfil_usuario,
                        "regla_multimedia": regla_multimedia
                    })
                    respuesta_raw = response["answer"]

                    if "[MOSTRAR_IMAGEN:" in respuesta_raw:
                        try:
                            ruta_imagen = respuesta_raw.split("[MOSTRAR_IMAGEN:")[1].split("]")[0].strip()
                            texto_limpio = respuesta_raw.split("[MOSTRAR_IMAGEN:")[0].strip() + respuesta_raw.split("]")[1].strip()
                            st.image(ruta_imagen, use_container_width=True, caption="Nuestra Habitacion")
                            st.markdown(texto_limpio)
                        except IndexError:
                            st.markdown(respuesta_raw)

                # Caso A: Captura Comercial (Lead)
                    if "[REGISTRAR_LEAD:" in respuesta_raw:
                        texto_limpio = respuesta_raw.split("[REGISTRAR_LEAD:")[0].strip()
                        motivo = respuesta_raw.split("[REGISTRAR_LEAD:")[1].replace("]", "").strip()
                    
                        st.markdown(texto_limpio)
                        st.session_state.messages.append({"role": "assistant", "content": texto_limpio})
                    
                    # Formulario embebido nativo de Streamlit
                        with st.form("form_lead"):
                            st.write("📝 **Deje sus datos para asignarle un asesor experto:**")
                            nombre = st.text_input("Nombre completo")
                            contacto = st.text_input("Correo o Teléfono")
                            submit = st.form_submit_button("Solicitar Atención Personalizada")
                            if submit:
                                registrar_evento_sistema("leads_seguimiento.csv", ["Fecha", "Nombre", "Contacto", "Motivo"], [datetime.now(), nombre, contacto, motivo])
                                st.success("✨ ¡Datos transferidos! Un asesor se comunicará con usted pronto.")
                                st.session_state.bloqueado = True
                                st.rerun()

                # Caso B: Gestión de Reclamos (Quejas)
                    elif "[ALERTA_QUEJA:" in respuesta_raw:
                        texto_limpio = respuesta_raw.split("[ALERTA_QUEJA:")[0].strip()
                        incidencia = respuesta_raw.split("[ALERTA_QUEJA:")[1].replace("]", "").strip()
                    
                        st.markdown(texto_limpio)
                        st.session_state.messages.append({"role": "assistant", "content": texto_limpio})
                    
                    # Petición de número de villa integrada
                        villa = st.text_input("Confirme su número de villa para enviar asistencia técnica inmediata:", key="villa_input")
                        if st.button("Enviar Alerta Prioritaria"):
                            registrar_evento_sistema("incidentes_criticos.csv", ["Fecha", "Villa", "Incidencia"], [datetime.now(), villa, incidencia])
                            st.warning("🚨 Reporte técnico enviado con éxito al Supervisor de Turno.")

                # Caso C: Proyección de Imágenes incorporadas
                    elif "[MOSTRAR_IMAGEN:" in respuesta_raw:
                        texto_limpio = respuesta_raw.split("[MOSTRAR_IMAGEN:")[0].strip()
                        url_img = respuesta_raw.split("[MOSTRAR_IMAGEN:")[1].replace("]", "").strip()
                    
                        st.markdown(texto_limpio)
                        st.image(url_img, caption="Instalaciones del Resort", use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "content": texto_limpio})

                # Caso D: Proyección de Videos
                    elif "[MOSTRAR_VIDEO:" in respuesta_raw:
                        texto_limpio = respuesta_raw.split("[MOSTRAR_VIDEO:")[0].strip()
                        url_vid = respuesta_raw.split("[MOSTRAR_VIDEO:")[1].replace("]", "").strip()
                    
                        st.markdown(texto_limpio)
                        st.video(url_vid)
                        st.session_state.messages.append({"role": "assistant", "content": texto_limpio})

                # Caso Común: Texto Plano
                    else:
                        st.markdown(respuesta_raw)
                        st.session_state.messages.append({"role": "assistant", "content": respuesta_raw})
                except Exception as e:
                    st.error(f" Error Interno Real: {e}")
                    mensaje_emergencia = "Disculpa, en este momento el sistema tiene alta demanda de usuarios. Podrias volver a intentarlo mas tarde. Gracias y disculpa las molestias"
                    st.markdown(mensaje_emergencia)
                    print(f"Error tecnico interceptado: {e}")
