import streamlit as st
import re
from datetime import date
from fpdf import FPDF
import unicodedata

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Diagnóstico de Retiro Patrimonial",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ESTILOS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
    :root { color-scheme: light; }
    .main .block-container {
        max-width: 1120px;
        padding-top: 1.35rem;
        padding-bottom: 2rem;
        padding-left: clamp(0.85rem, 3vw, 2rem);
        padding-right: clamp(0.85rem, 3vw, 2rem);
    }
    .main-header {
        background: linear-gradient(125deg, #101d35 0%, #203d60 72%, #8d713d 100%);
        padding: clamp(1rem, 2.5vw, 1.8rem);
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 1rem;
        text-align: left;
        border: 1px solid rgba(201, 168, 100, .4);
        box-shadow: 0 7px 20px rgba(16, 29, 53, .12);
    }
    .main-header h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: clamp(1.35rem, 3.2vw, 2.05rem);
        line-height: 1.2;
        font-weight: 750;
    }
    .main-header p {
        color: #e1e7ef !important;
        margin: .45rem 0 0 0;
        font-size: clamp(.9rem, 1.7vw, 1.05rem);
        line-height: 1.4;
    }
    h2, h3 { color: #172d49; letter-spacing: -.015em; }
    h2 { margin-top: .9rem; }
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(16, 29, 53, .06);
        border: 1px solid #e1e7ef;
        border-left: 3px solid #b79a5b;
        margin-bottom: .85rem;
    }
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f3f6fa 100%);
        border-radius: 12px;
        padding: 1rem .65rem;
        text-align: center;
        border: 1px solid #dfe6ef;
        height: 100%;
        box-sizing: border-box;
    }
    .metric-card h3 {
        color: #526174 !important;
        font-size: .74rem;
        line-height: 1.35;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: .035em;
    }
    .metric-card .value {
        color: #183554 !important;
        font-size: clamp(1.25rem, 2.6vw, 1.75rem);
        line-height: 1.2;
        overflow-wrap: anywhere;
        font-weight: 750;
        margin: .45rem 0;
    }
    .metric-card .label { color: #657286 !important; font-size: .78rem; line-height: 1.35; }
    .success-box, .warning-box, .info-box, .note-box {
        padding: .8rem .95rem;
        border-radius: 9px;
        margin: .75rem 0;
        line-height: 1.5;
        font-size: .92rem;
    }
    .success-box { background: #f0f7f2; color: #214d35; border-left: 3px solid #5d9470; }
    .warning-box { background: #fbf7ee; color: #624d24; border-left: 3px solid #b99b5b; }
    .info-box { background: #f1f5f9; color: #33465d; border-left: 3px solid #7188a4; }
    .note-box { background: #f7f8fa; color: #5b6573; border: 1px solid #e3e7ed; font-size: .8rem; }
    .stButton > button, .stDownloadButton > button {
        background: #183554;
        color: #ffffff !important;
        border: 1px solid #183554;
        padding: .58rem 1rem;
        border-radius: 8px;
        font-weight: 650;
        font-size: .94rem;
        min-height: 2.65rem;
        width: 100%;
        transition: background .15s ease, border-color .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #294b70;
        color: #ffffff !important;
        border-color: #294b70;
    }
    .stButton > button:focus, .stDownloadButton > button:focus {
        box-shadow: 0 0 0 2px #d8c391;
        outline: none;
    }
    div[data-testid="stMetricValue"] { color: #183554 !important; font-weight: 750; }
    div[data-testid="stAlert"] { border-radius: 9px; padding: .65rem .8rem; }
    .stCaption, [data-testid="stCaptionContainer"] { line-height: 1.45; color: #647184; }
    label, [data-testid="stWidgetLabel"] p { color: #24364b !important; font-weight: 550; }
    input, textarea, [data-baseweb="select"] > div {
        border-radius: 8px !important;
    }
    input, textarea { font-size: 16px !important; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input, [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #172b43 !important;
        border-color: #cbd5e1 !important;
    }
    [data-testid="stTextInput"] input::placeholder { color: #7b8797 !important; }
    [data-baseweb="select"] * { color: #172b43; }
    [data-testid="stExpander"] { border-color: #e0e6ed; border-radius: 9px; }
    [data-testid="stHorizontalBlock"] { gap: .85rem; }
    @media (max-width: 700px) {
        .main .block-container { padding-top: .65rem; padding-left: .8rem; padding-right: .8rem; }
        .main-header { padding: 1rem; border-radius: 11px; }
        .main-header p { margin-top: .4rem; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .5rem; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
        .metric-card { padding: .85rem .65rem; }
        .metric-card .value { font-size: 1.45rem; }
        .stButton > button, .stDownloadButton > button { min-height: 2.45rem; padding: .55rem .75rem; font-size: .9rem; }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1.08rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES FINANCIERAS
# ==========================================
RENDIMIENTO_ANUAL_AFORE = 0.05
COMISION_ANUAL_AFORE = 0.00538
DENSIDAD_COTIZACION = 0.8
MARGEN_SEGURIDAD = 0.02
FACTOR_PENSION_97 = 1.15
TOPE_BIENESTAR = 17364.00
UMA_ANUAL_2026 = 42818.15
LIMITE_5_UMAS = UMA_ANUAL_2026 * 5
LIMITE_ART_185 = 152000.00
RENDIMIENTO_PLAN_SUGERIDO = 0.11
MINIMO_APORTACION = 2000.0

ANUALIDADES = {
    "Hombre": {60: 15.8, 65: 14.85},
    "Mujer": {60: 17.2, 65: 15.5}
}

tasa_mensual_neta_afore = (RENDIMIENTO_ANUAL_AFORE - COMISION_ANUAL_AFORE) / 12
tasa_mensual_comp = (1 + RENDIMIENTO_PLAN_SUGERIDO) ** (1/12) - 1


def texto_pdf_seguro(texto):
    """Convierte texto a caracteres compatibles con las fuentes PDF estándar."""
    texto = str(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.encode("latin-1", errors="replace").decode("latin-1")

# ==========================================
# ENCABEZADO Y AVISO DE PRIVACIDAD
# ==========================================
try:
    col_logo, col_titulo = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        st.image("logo.png", use_container_width=True)
    with col_titulo:
        st.markdown("""
        <div class="main-header">
            <h1>Diagnóstico de Retiro Patrimonial</h1>
            <p>Una primera aproximación para entender tu pensión y planear tu futuro financiero.</p>
        </div>
        """, unsafe_allow_html=True)
except Exception:
    st.markdown("""
    <div class="main-header">
        <h1>Diagnóstico de Retiro Patrimonial</h1>
        <p>Una primera aproximación para entender tu pensión y planear tu futuro financiero.</p>
    </div>
    """, unsafe_allow_html=True)

st.caption("Diagnóstico ilustrativo elaborado con los datos capturados. Los resultados pueden variar y deben revisarse durante la asesoría.")

with st.expander("Consultar aviso de privacidad simplificado"):
    st.markdown("""
    **Responsable del tratamiento:** Iván Lenz, asesor patrimonial independiente.

    **Datos que se solicitan:** nombre, teléfono y datos generales laborales y financieros que captures voluntariamente.

    **Finalidad:** elaborar un diagnóstico estimado de retiro y, cuando corresponda, preparar un reporte PDF para entregártelo y dar seguimiento a la consulta que solicitaste.

    **Uso y resguardo:** los datos deben tratarse únicamente para estas finalidades y no deben compartirse con terceros ajenos al servicio sin una base legal aplicable o tu autorización. No introduzcas contraseñas, números completos de identificación ni información que no sea necesaria.

    **Derechos y contacto:** para solicitar acceso, rectificación, cancelación u oponerte al tratamiento, contacta al asesor que te compartió este formulario por el mismo medio.

    **Importante:** este texto es un aviso simplificado provisional; antes de publicar o distribuir ampliamente la aplicación, debe completarse con los datos de contacto, medios de ejercicio de derechos y demás elementos legales aplicables.
    """)

acepta_privacidad = st.checkbox(
    "He leído el aviso de privacidad y autorizo el uso de los datos que capture para elaborar mi diagnóstico.",
    value=False,
    help="El formulario no mostrará los campos de captura hasta que marques esta casilla."
)

if acepta_privacidad:
    st.markdown("### 1. Identifiquemos tu régimen")
    fecha_primera_cotizacion = st.date_input(
        "¿Cuándo comenzaste a cotizar ante el IMSS?",
        value=None,
        min_value=date(1960, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY",
        help="Si no conoces la fecha exacta, revisa tu Constancia de Semanas Cotizadas del IMSS."
    )
    st.caption("La fecha ayuda a identificar el régimen que debemos revisar. Si cotizaste antes del 1 de julio de 1997, revisaremos tu caso con un diagnóstico específico.")
    if fecha_primera_cotizacion is not None and fecha_primera_cotizacion < date(1997, 7, 1):
        st.warning("Por la fecha capturada, podrías pertenecer al régimen de transición (Ley 73) o tener derecho a elegir régimen. Este formulario no realizará el cálculo Ley 97. Se requiere un diagnóstico específico de Ley 73 / transición.")
    elif fecha_primera_cotizacion is not None:
        st.success("La fecha capturada es a partir del 1 de julio de 1997. Puedes continuar con este diagnóstico preliminar de Ley 97; verifica la fecha contra tu constancia oficial.")

    modo_vista = st.sidebar.selectbox("Modo de Vista", ["Cliente (Pública)", "Asesor (Privada)"], help="El modo asesor habilita un campo adicional para capturar semanas cotizadas reales.")

    # ==========================================
    # PASO 1: DATOS PERSONALES
    # ==========================================
    st.markdown("### 2. Tus datos")
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre completo", placeholder="Ej. Beatriz Díaz", help="Se utiliza para identificar el reporte PDF. Captura tu nombre como deseas que aparezca en el documento.")
        telefono = st.text_input("Teléfono celular (10 dígitos)", placeholder="Ej. 3312345678", help="Permite dar seguimiento a la consulta. Escribe únicamente los 10 dígitos, sin espacios ni guiones.")
        telefono_valido = bool(re.match(r"^\d{10}$", telefono)) if telefono else False
        if telefono and not telefono_valido:
            st.warning("⚠️ El teléfono debe contener exactamente 10 números.")

    with col2:
        sexo = st.radio("Sexo", ["Hombre", "Mujer"], horizontal=True, help="Se usa para seleccionar el factor actuarial de referencia que contiene el modelo actual.")
        edad_actual = st.number_input("Edad actual", min_value=18, max_value=64, value=40, step=1, help="Edad en años cumplidos. El modelo estima el horizonte hasta los 65 años.")
        st.caption("La fecha exacta de primera cotización se captura arriba para validar el régimen. Esta validación no sustituye la constancia oficial del IMSS.")

    # ==========================================
    # PASO 2: DATOS FINANCIEROS
    # ==========================================
    st.markdown("---")
    st.markdown("### 3. Tu situación financiera")
    col3, col4 = st.columns(2)

    with col3:
        salario_mensual = st.number_input("Sueldo mensual bruto actual (MXN)", min_value=0.0, value=0.0, step=1000.0, format="%.2f", help="Captura el ingreso mensual antes de impuestos y descuentos. El modelo lo usa como referencia para estimar la pensión y la brecha de ingreso.")
        if salario_mensual > 0:
            st.caption(f"**${salario_mensual:,.2f} MXN**")

    with col4:
        saldo_afore = st.number_input("Saldo actual en tu AFORE (MXN)", min_value=0.0, value=0.0, step=5000.0, format="%.2f", help="Consulta el saldo en tu estado de cuenta de AFORE. Usa el saldo de retiro/cesantía/vejez (RCV) cuando esté desglosado; evita sumar subcuentas que no correspondan.")
        if saldo_afore > 0:
            st.caption(f"**${saldo_afore:,.2f} MXN**")

    # ==========================================
    # PASO 3: PERFIL LABORAL
    # ==========================================
    st.markdown("---")
    st.markdown("### 4. Información laboral complementaria")
    es_empleado_imss = st.checkbox("¿Eres trabajador de base del propio IMSS, contratado después del 1 de agosto de 2008?", help="Marca esta opción únicamente si eres personal de base del Instituto Mexicano del Seguro Social y aplica la retención descrita abajo.")

    porcentaje_ahorro_imss = 0.11 if es_empleado_imss else 0.0
    saldo_voluntario_actual = 0.0

    if es_empleado_imss:
        st.markdown("""
        <div class="info-box">
        <strong>Referencia:</strong> Para personal de base del IMSS contratado después de agosto de 2008, el modelo considera la retención del 11% indicada para este escenario.
        </div>
        """, unsafe_allow_html=True)
        saldo_voluntario_actual = st.number_input("Saldo actual del ahorro por tarjetón / ahorro voluntario (MXN)", min_value=0.0, value=0.0, step=5000.0, format="%.2f", help="Captura el saldo acumulado que corresponda a este ahorro, según el estado de cuenta disponible. Si no lo conoces, solicita confirmación antes de usar el resultado como definitivo.")
        if saldo_voluntario_actual > 0:
            st.caption(f"**${saldo_voluntario_actual:,.2f} MXN**")

    # ==========================================
    # PASO 4: ESTRATEGIA FISCAL
    # ==========================================
    st.markdown("---")
    st.markdown("### 5. Preferencia fiscal")
    quiere_deducir = st.radio(
        "¿Qué escenario fiscal quieres revisar?",
        ["Sí, quiero deducir y estimar una posible devolución anual",
         "No, prefiero explorar una opción sin deducción actual"],
        help="Esta selección sirve para comparar escenarios durante la asesoría. El tratamiento fiscal depende del plan y de los requisitos aplicables."
    )

    semanas_cotizadas = 0
    if modo_vista == "Asesor (Privada)":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Panel del Asesor")
        semanas_cotizadas = st.sidebar.number_input("Semanas cotizadas reales", min_value=0, value=1000, help="Dato de la Constancia de Semanas Cotizadas del IMSS. El cálculo actual no usa este campo en las fórmulas; se conserva para referencia del asesor.")

    # ==========================================
    # BOTÓN DE CÁLCULO
    # ==========================================
    st.markdown("---")
    st.caption("Revisa los datos y calcula tu estimación. Durante la asesoría podrás revisar cada resultado.")
    if st.button("Calcular mi diagnóstico", type="primary"):
        if fecha_primera_cotizacion is None:
            st.error("Selecciona la fecha de tu primera cotización registrada ante el IMSS para validar el régimen antes de calcular.")
        elif fecha_primera_cotizacion < date(1997, 7, 1):
            st.error("Cálculo bloqueado: la fecha capturada corresponde a una posible situación de Ley 73 / transición. No se generará un diagnóstico Ley 97 con estos datos.")
        elif not nombre or not telefono_valido:
            st.error("Por favor, revisa que tu nombre y teléfono a 10 dígitos estén bien escritos.")
        elif salario_mensual == 0:
            st.error("Por favor, ingresa tu sueldo mensual actual.")
        else:
            with st.spinner("Calculando tu diagnóstico..."):
                anos_futuros = 65 - edad_actual
                meses_totales = anos_futuros * 12
                factor_calibracion = 0.942

                saldo_afore_acumulado = saldo_afore
                for mes in range(1, meses_totales + 1):
                    ano_simulado = 2026 + (mes // 12)
                    if ano_simulado == 2026: tasa_cotiz = 0.10638
                    elif ano_simulado == 2027: tasa_cotiz = 0.11728
                    elif ano_simulado == 2028: tasa_cotiz = 0.12819
                    elif ano_simulado == 2029: tasa_cotiz = 0.13909
                    else: tasa_cotiz = 0.15000

                    aportacion_mes = salario_mensual * tasa_cotiz * DENSIDAD_COTIZACION * factor_calibracion
                    saldo_afore_acumulado = (saldo_afore_acumulado * (1 + tasa_mensual_neta_afore)) + aportacion_mes

                ae_65_fija = ANUALIDADES[sexo][65]
                pension_65_base = (saldo_afore_acumulado / ((1 + MARGEN_SEGURIDAD) * ae_65_fija)) * FACTOR_PENSION_97 / 12
                complemento_solidario = max(0.0, TOPE_BIENESTAR - pension_65_base) if pension_65_base < TOPE_BIENESTAR else 0.0
                pension_65_obligatoria_total = pension_65_base + complemento_solidario

                saldo_voluntario_acumulado = saldo_voluntario_actual
                for mes in range(1, meses_totales + 1):
                    aportacion_voluntaria_tarjeton = salario_mensual * porcentaje_ahorro_imss
                    saldo_voluntario_acumulado = (saldo_voluntario_acumulado * (1 + tasa_mensual_neta_afore)) + aportacion_voluntaria_tarjeton

                pension_generada_voluntario = (saldo_voluntario_acumulado / ((1 + MARGEN_SEGURIDAD) * ae_65_fija)) * FACTOR_PENSION_97 / 12

                pension_afore_consolidada = pension_65_obligatoria_total + pension_generada_voluntario
                brecha_patrimonial = max(0.0, salario_mensual - pension_afore_consolidada)
                tasa_reemplazo = (pension_afore_consolidada / salario_mensual) * 100 if salario_mensual > 0 else 0

                capital_necesario_comp = 0.0
                aportacion_final_comp = 0.0
                pension_generada_ahorro = 0.0
                devolucion_texto_reporte = "$0.00 MXN"
                devolucion_estimada = 0.0

                # ==========================================
                # RESULTADOS VISUALES
                # ==========================================
                st.markdown("---")
                st.markdown("## 📊 Tu Diagnóstico de Retiro")

                col_a, col_b, col_c = st.columns([1, 1, 1])
                with col_a:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Pensión obligatoria estimada</h3>
                        <div class="value">${pension_65_obligatoria_total:,.0f}</div>
                        <div class="label">MXN mensuales</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Ingreso cubierto por la pensión</h3>
                        <div class="value">{tasa_reemplazo:.1f}%</div>
                        <div class="label">AFORE y, si aplica, ahorro IMSS</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Diferencia mensual estimada</h3>
                        <div class="value">${brecha_patrimonial:,.0f}</div>
                        <div class="label">MXN por cubrir</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Sección 1
                st.markdown("---")
                st.markdown("### 1. Tu pensión del sistema obligatorio")
                st.write(f"- Fondo estimado acumulado por Ley: **${saldo_afore_acumulado:,.2f} MXN**")
                st.write(f"- Pensión base de la Afore: **${pension_65_base:,.2f} MXN**")
                if complemento_solidario > 0:
                    st.write(f"- Subsidio del Gobierno (Fondo del Bienestar): **${complemento_solidario:,.2f} MXN**")
                st.write(f"- **Pensión mensual obligatoria estimada: ${pension_65_obligatoria_total:,.2f} MXN**")
                st.caption("Este resultado se calcula con la proyección del sistema obligatorio. No depende de la opción fiscal ni de contratar un plan privado.")

                # Sección 2 (solo si es IMSS)
                if es_empleado_imss:
                    st.markdown("---")
                    st.markdown("### Ahorro complementario de nómina IMSS")
                    st.write(f"- Fondo total estimado de Ahorro Voluntario a los 65 años: **${saldo_voluntario_acumulado:,.2f} MXN**")
                    st.write(f"- **Pensión mensual extra generada por tu Ahorro Voluntario: ${pension_generada_voluntario:,.2f} MXN**")

                # Sección 3
                st.markdown("---")
                st.markdown("### 2. La diferencia entre tu ingreso actual y tu pensión")

                if es_empleado_imss:
                    st.write(f"Hoy ganas **${salario_mensual:,.2f} MXN**, pero sumando tu Afore Obligatoria y tu Ahorro Voluntario solo cubres el **{tasa_reemplazo:.1f}%** de tus ingresos.")
                else:
                    st.write(f"Hoy ganas **${salario_mensual:,.2f} MXN**, pero tu Afore Obligatoria solo cubre el **{tasa_reemplazo:.1f}%** de tus ingresos.")

                if brecha_patrimonial > 0:
                    st.markdown(f"""
                    <div class="warning-box">
                    <strong>Te harán falta cada mes: ${brecha_patrimonial:,.2f} MXN.</strong><br>
                    Esta es la diferencia mensual estimada entre tu ingreso actual y la pensión proyectada.
                    </div>
                    """, unsafe_allow_html=True)

                    # Sección 4
                    st.markdown("---")
                    st.markdown("### 3. Una estrategia para complementar tu pensión")
                    capital_necesario_comp = (brecha_patrimonial * 12 * ae_65_fija * (1 + MARGEN_SEGURIDAD)) / FACTOR_PENSION_97

                    if meses_totales > 0:
                        factor_acumulacion = ((1 + tasa_mensual_comp) ** meses_totales - 1) / tasa_mensual_comp
                        aportacion_requerida = capital_necesario_comp / factor_acumulacion
                    else:
                        aportacion_requerida = 0.0

                    aportacion_final_comp = max(MINIMO_APORTACION, aportacion_requerida)
                    pension_generada_ahorro = (capital_necesario_comp * FACTOR_PENSION_97) / (ae_65_fija * (1 + MARGEN_SEGURIDAD)) / 12

                    st.write(f"- **Fondo privado proyectado: ${capital_necesario_comp:,.2f} MXN**")
                    st.metric(label="Ahorro mensual sugerido", value=f"${aportacion_final_comp:,.2f} MXN")
                    st.caption("Esta propuesta busca complementar la pensión estimada y acercarte al ingreso mensual que deseas en el retiro. Es un escenario ilustrativo, no una obligación de contratación.")

                    # Sección 5
                    st.markdown("---")
                    st.markdown("### Resultado combinado de los escenarios")
                    pension_consolidada_final = pension_65_obligatoria_total + pension_generada_voluntario + pension_generada_ahorro

                    st.markdown(f"""
                    <div class="success-box">
                    <strong>INGRESO MENSUAL TOTAL ESTIMADO AL RETIRO</strong><br>
                    <span style="font-size: 2rem; font-weight: 700; color: #1e3a5f;">${pension_consolidada_final:,.2f} MXN</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write(f"• (+) Pensión por tu Afore Obligatoria de Ley: **${pension_65_obligatoria_total:,.2f} MXN**")
                    if es_empleado_imss:
                        st.write(f"• (+) Pensión extra por tu Ahorro Voluntario IMSS: **${pension_generada_voluntario:,.2f} MXN**")
                    st.write(f"• (+) Pensión estimada por tu Plan Privado Sugerido: **${pension_generada_ahorro:,.2f} MXN**")

                    # Sección 6
                    if "Sí, quiero deducir" in quiere_deducir:
                        st.markdown("---")
                        st.markdown("### 4. Estimación fiscal ilustrativa")
                        tasa_calculada = 0.15 if salario_mensual <= 25000 else (0.20 if salario_mensual <= 40000 else (0.30 if salario_mensual <= 90000 else 0.35))

                        ahorro_anual_plan = aportacion_final_comp * 12
                        ingreso_anual_estimado = salario_mensual * 12
                        ahorro_imss_anual_retencion = ingreso_anual_estimado * porcentaje_ahorro_imss

                        tope_10_porciento = ingreso_anual_estimado * 0.10
                        tope_legal_art151 = min(tope_10_porciento, LIMITE_5_UMAS)

                        if es_empleado_imss and ahorro_imss_anual_retencion >= tope_legal_art151:
                            st.write(f"• **Filtro Especial de Nómina IMSS:** Tu retención por tarjetón ({porcentaje_ahorro_imss*100:.1f}%) ya satura tu tope legal del Artículo 151.")
                            st.write("• **Solución Técnica:** Este plan alterno se registrará bajo el **Artículo 185 (CEA)**, liberándote un espacio libre extra de **$152,000.00 MXN anuales**.")
                            monto_deducible_real = min(ahorro_anual_plan, LIMITE_ART_185)
                        else:
                            monto_deducible_real = min(ahorro_anual_plan, tope_legal_art151)

                        devolucion_estimada = monto_deducible_real * tasa_calculada
                        devolucion_texto_reporte = f"${devolucion_estimada:,.2f} MXN"
                        st.metric(label="Posible recuperación fiscal anual", value=devolucion_texto_reporte)
                        st.write(f"Costo mensual estimado después de la recuperación ilustrativa: **${(aportacion_final_comp - (devolucion_estimada/12)):,.2f} MXN**")
                        st.markdown('<div class="note-box">Estimación sujeta a tu situación fiscal, al monto deducible y al cumplimiento de los requisitos aplicables. No representa una devolución garantizada.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("---")
                        st.markdown("### 4. Escenario sin deducción actual")
                        st.write("Esta alternativa permite revisar un esquema que no busca una deducción fiscal hoy.")
                        st.markdown('<div class="note-box">El tratamiento fiscal al retiro depende del plan contratado y de cumplir sus requisitos. La exención no aplica automáticamente a cualquier ahorro.</div>', unsafe_allow_html=True)

                else:
                    st.success("Según los datos capturados, la pensión estimada cubre el ingreso mensual indicado.")
                    pension_consolidada_final = pension_65_obligatoria_total + pension_generada_voluntario

                # ==========================================
                # GENERACIÓN DEL PDF
                # ==========================================
                st.markdown("---")
                st.subheader("📄 Exportar Reporte Ejecutivo")

                class PDF(FPDF):
                    def header(self):
                        try:
                            self.image("logo.png", x=10, y=8, w=20)
                        except:
                            pass
                        self.set_font('Helvetica', 'B', 14)
                        self.cell(0, 10, 'DIAGNOSTICO CONSULTIVO DE RETIRO PATRIMONIAL', ln=True, align='C')
                        self.ln(5)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Helvetica', 'I', 8)
                        self.cell(0, 10, f'Pagina {self.page_no()} | Ivan Lenz - Asesor Patrimonial', align='C')

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=11)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "1. INFORMACION DEL ASEGURADO", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.cell(0, 6, texto_pdf_seguro(f"Nombre: {nombre}"), ln=True)
                pdf.cell(0, 6, f"Telefono: {telefono}", ln=True)
                pdf.cell(0, 6, f"Sexo: {sexo} | Edad actual: {edad_actual} anos", ln=True)
                pdf.cell(0, 6, f"Primera cotizacion IMSS capturada: {fecha_primera_cotizacion.strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 6, "Regimen evaluado por fecha capturada: Ley 97 (validar con constancia oficial)", ln=True)
                pdf.cell(0, 6, f"Sueldo Mensual Bruto: {salario_mensual:,.2f} MXN", ln=True)
                pdf.ln(5)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "2. DIAGNOSTICO DEL SISTEMA OBLIGATORIO (AFORE)", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.cell(0, 6, f"Fondo estimado acumulado: {saldo_afore_acumulado:,.2f} MXN", ln=True)
                pdf.cell(0, 6, f"Pension base de la Afore: {pension_65_base:,.2f} MXN", ln=True)
                if complemento_solidario > 0:
                    pdf.cell(0, 6, f"Complemento del Bienestar: {complemento_solidario:,.2f} MXN", ln=True)
                pdf.cell(0, 6, f"Pension Mensual Obligatoria: {pension_65_obligatoria_total:,.2f} MXN", ln=True)
                pdf.ln(5)

                if es_empleado_imss:
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 8, "3. AHORRO VOLUNTARIO (TARJETON)", ln=True)
                    pdf.set_font("Helvetica", size=11)
                    pdf.cell(0, 6, f"Fondo total estimado: {saldo_voluntario_acumulado:,.2f} MXN", ln=True)
                    pdf.cell(0, 6, f"Pension mensual extra: {pension_generada_voluntario:,.2f} MXN", ln=True)
                    pdf.ln(5)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "4. ANALISIS DE LA BRECHA", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.cell(0, 6, f"Tasa de reemplazo: {tasa_reemplazo:.1f}%", ln=True)
                pdf.cell(0, 6, f"Brecha mensual: {brecha_patrimonial:,.2f} MXN", ln=True)
                pdf.ln(5)

                if brecha_patrimonial > 0:
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 8, "5. PLAN DE AHORRO PRIVADO SUGERIDO", ln=True)
                    pdf.set_font("Helvetica", size=11)
                    pdf.cell(0, 6, f"Fondo de Reserva a Construir: {capital_necesario_comp:,.2f} MXN", ln=True)
                    pdf.cell(0, 6, f"Ahorro Mensual Sugerido: {aportacion_final_comp:,.2f} MXN", ln=True)
                    pdf.cell(0, 6, f"Pension estimada por el Plan Privado: {pension_generada_ahorro:,.2f} MXN", ln=True)
                    pdf.ln(5)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "6. RESUMEN CONSOLIDADO DE PENSION MENSUAL FUTURA", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.cell(0, 6, f"(+) Afore Obligatoria: {pension_65_obligatoria_total:,.2f} MXN", ln=True)
                if es_empleado_imss:
                    pdf.cell(0, 6, f"(+) Ahorro Voluntario: {pension_generada_voluntario:,.2f} MXN", ln=True)
                if brecha_patrimonial > 0:
                    pdf.cell(0, 6, f"(+) Plan Privado Sugerido: {pension_generada_ahorro:,.2f} MXN", ln=True)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"PENSION TOTAL MENSUAL: {pension_consolidada_final:,.2f} MXN", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.ln(5)

                if "Sí, quiero deducir" in quiere_deducir and brecha_patrimonial > 0:
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 8, "7. ESTIMACION DE RECUPERACION DE IMPUESTOS", ln=True)
                    pdf.set_font("Helvetica", size=11)
                    pdf.cell(0, 6, f"Saldo a favor estimado: {devolucion_texto_reporte}", ln=True)
                    pdf.ln(5)

                pdf.ln(10)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 5, "AVISO: Resultados hipoteticos e ilustrativos; no representan una pension garantizada ni una resolucion oficial. La estimacion fiscal depende de la situacion del contribuyente, el plan contratado y los requisitos aplicables.")

                pdf_output = bytes(pdf.output())
                st.download_button(
                    label="📥 Descargar Diagnóstico Patrimonial en PDF",
                    data=bytes(pdf_output),
                    file_name=f"Plan_Retiro_{re.sub(r'[^A-Za-z0-9_-]+', '_', texto_pdf_seguro(nombre)).strip('_') or 'Prospecto'}.pdf",
                    mime="application/pdf"
                )

                st.markdown("---")
                st.caption("Nota: resultados ilustrativos. La pensión debe validarse con la información oficial del IMSS/AFORE. Las estimaciones fiscales dependen del plan y de los requisitos aplicables.")
else:
    st.info("Para comenzar, consulta el aviso de privacidad y marca la casilla de autorización. No se mostrarán los campos de captura hasta que lo hagas.")
