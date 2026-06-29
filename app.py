import os
import csv
from datetime import datetime
import streamlit as st

# Componentes de Orquestación de IA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

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
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
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

            # Construir e invocar la cadena de IA
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
            system_prompt = (
                f"Eres el Concierge de Bienestar de 'Aura Vitalis Eco-Resort & Spa'.\n"
                f"El usuario interactuando es un: {perfil_usuario}\n"
                f"Regla de Control de Medios: {regla_multimedia}\n\n"
                "JERARQUÍA:\n"
                "1. Si preguntan datos del manual (horarios, políticas, wifi), responde directo sin pedir datos ni etiquetas.\n"
                "2. INDECISIÓN COMERCIAL: Si duda en reservar, pide NOMBRE y CONTACTO. Al final agrega: '[REGISTRAR_LEAD: Motivo]'.\n"
                "3. RECLAMOS: Si está molesto, discúlpate empáticamente y agrega al final: '[ALERTA_QUEJA: Detalles]'.\n"
                "Contexto:\n{context}"
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