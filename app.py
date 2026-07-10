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
        regla_multimedia = "Puedes desplegar el video corporativo usando la etiqueta [MOSTRAR_VIDEO] si piden ver el hotel."

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
                        if response.status_code == 200:         
                     
                        res_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                        # --- NUEVA LÍNEA: Interceptar datos y limpiar texto ---
                        res_text = guardar_datos_csv(res_text)
                        return AIMessage(content=res_text)
                    else:
                        raise Exception(f"Error en Gemini API: {response.text}")
            llm = NativeGeminiChat()

            system_prompt = (
                f"Eres el Concierge de Bienestar de 'Aura Vitalis Eco-Resort & Spa'.\n"
                f"El usuario interactuando es un: {perfil_usuario}\n"
                f"Regla de Control de Medios: {regla_multimedia}\n\n"
                "JERARQUÍA:\n"
                "1. Si preguntan datos del manual (horarios, políticas, wifi), responde directo sin pedir datos ni etiquetas.\n"
                "2. INDECISIÓN COMERCIAL: Si duda en reservar, pide NOMBRE y CONTACTO. Al final agrega: '[REGISTRAR_LEAD: Motivo]'.\n"
                "3. RECLAMOS: Si está molesto, discúlpate empáticamente y agrega al final: '[ALERTA_QUEJA: Detalles]'.\n"
                "4. Contexto:\n{context}"
                "5. CHECK-IN DIGITAL: Si un usuario con reserva confirmada desea hacer check-in, pídele su nombre completo y hora estimada de llegada. Finaliza diciendo: 'Su pre-registro está listo, lo esperamos con una bebida de bienvenida.' y agrega: '[REGISTRAR_CHECKIN: Nombre - Hora LLegada]'.\n"
                "6. CHECK-OUT EXPRESS: Si un huésped desea entregar la habitación, pídele su número de habitación. Finaliza diciendo: 'Hemos procesado su salida. El personal de botones va por su equipaje. ¡Buen viaje!' y agrega: '[ALERTA_CHECKOUT: Habitación]'.\n"
            )
            
            prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
            rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt_template))
            
            response = rag_chain.invoke({"input": prompt_usuario})
            respuesta_raw = response["answer"]

            # --- PROCESAR INTERCEPTORES EN LA INTERFAZ GRÁFICA ---
            with st.chat_message("assistant"):
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
