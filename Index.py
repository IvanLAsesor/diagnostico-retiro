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
    .main-header {
        background: linear-gradient(135deg, #101d35 0%, #1e3a5f 70%, #9b7a3c 100%);
        padding: clamp(1.2rem, 3vw, 2.2rem);
        border-radius: 14px;
        color: white;
        margin-bottom: 1.4rem;
        text-align: left;
        border: 1px solid rgba(201, 168, 100, .45);
        box-shadow: 0 10px 28px rgba(16, 29, 53, .14);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: clamp(1.45rem, 3vw, 2.15rem);
        line-height: 1.2;
        font-weight: 750;
    }
    .main-header p {
        color: #cbd5e0;
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #2c5282;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        max-width: 280px;
        margin: 0 auto;
    }
    .metric-card h3 {
        color: #4a5568;
        font-size: 0.8rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        color: #1e3a5f;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-card .label {
        color: #718096;
        font-size: 0.8rem;
    }
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        max-width: 600px;
    }
    .warning-box {
        background: #fffaf0;
        border-left: 4px solid #dd6b20;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        max-width: 600px;
    }
    .info-box {
        background: #ebf8ff;
        border-left: 4px solid #3182ce;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        max-width: 600px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #101d35 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #1e3a5f;
        font-weight: 700;
    }
    div[data-testid="stAlert"] { border-radius: 10px; }
    .stCaption, [data-testid="stCaptionContainer"] { line-height: 1.45; }
    @media (max-width: 700px) {
        .main-header { padding: 1.1rem; }
        .metric-card .value { font-size: 1.4rem; }
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
# ENCABEZADO
# ==========================================
try:
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        st.image("logo.png", width=120)
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

st.info("Este diagnóstico es una herramienta educativa de estimación. No sustituye una resolución del IMSS, una proyección oficial de la AFORE ni una asesoría fiscal individual.")

# ==========================================
# AVISO DE PRIVACIDAD SIMPLIFICADO
# ==========================================
with st.expander("📄 Consultar Aviso de Privacidad"):
    st.markdown("""
    ### Aviso de Privacidad Simplificado

    **Responsable:** Gabril Iván Lenz C, asesor patrimonial independiente.
    **Contacto:** ivanlenz@proton.me

    **Datos que se tratarán:**
    Esta herramienta **no solicita tu nombre, teléfono ni datos de identificación personal**. Únicamente captura:
    - Edad y sexo.
    - Sueldo mensual.
    - Saldo de AFORE y ahorro voluntario.
    - Semanas cotizadas (opcional, modo asesor).
    - Preferencia fiscal.

    **Finalidad:**
    Estos datos se utilizan **exclusivamente** para elaborar un diagnóstico estimado de tu retiro y generar un reporte en PDF. No se usarán para contactarte, ni para fines publicitarios, ni se compartirán con terceros.

    **Consentimiento:**
    Al marcar la casilla de aceptación, otorgas tu **consentimiento expreso** para el tratamiento de tus datos financieros con la única finalidad de realizar este cálculo.

    **Derechos ARCO:**
    Puedes solicitar acceso, rectificación, cancelación u oposición al tratamiento de tus datos enviando un correo a ivanlenz@proton.me.

    **Importante:** Este es un aviso simplificado. El aviso integral está disponible a solicitud.
    """)

acepta_privacidad = st.checkbox(
    "He leído el Aviso de Privacidad y autorizo el uso de mis datos financieros para elaborar mi diagnóstico.",
    value=False,
    help="El formulario no mostrará los campos de captura hasta que marques esta casilla."
)

if acepta_privacidad:
    st.markdown("### Antes de comenzar: identifica tu régimen")
    fecha_primera_cotizacion = st.date_input(
        "Fecha de tu primera cotización registrada ante el IMSS",
        value=date(1997, 7, 1),
        min_value=date(1960, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY",
        help="Busca la fecha de registro o el primer movimiento en tu Constancia de Semanas Cotizadas del IMSS o en la información de tu AFORE. La fecha en que empezaste a trabajar puede ser distinta."
    )
    st.caption("La fecha de referencia para distinguir los regímenes es el 1 de julio de 1997. Si cotizaste antes de esa fecha, el IMSS puede reconocer derechos de transición y este cálculo de Ley 97 no debe usarse sin revisar tu caso.")
    if fecha_primera_cotizacion is not None and fecha_primera_cotizacion < date(1997, 7, 1):
        st.warning("Por la fecha capturada, podrías pertenecer al régimen de transición (Ley 73) o tener derecho a elegir régimen. Este formulario no realizará el cálculo Ley 97. Se requiere un diagnóstico específico de Ley 73 / transición.")
    elif fecha_primera_cotizacion is not None:
        st.success("La fecha capturada es a partir del 1 de julio de 1997. Puedes continuar con este diagnóstico preliminar de Ley 97; verifica la fecha contra tu constancia oficial.")

    modo_vista = st.sidebar.selectbox("Modo de Vista", ["Cliente (Pública)", "Asesor (Privada)"], help="El modo asesor habilita un campo adicional para capturar semanas cotizadas reales.")

    # ==========================================
    # PASO 1: DATOS PERSONALES
    # ==========================================
    st.markdown("### 👤 Paso 1: Tus Datos")
    col1, col2 = st.columns(2)

    with col1:
        sexo = st.radio("Sexo", ["Hombre", "Mujer"], horizontal=True, help="Se usa para seleccionar el factor actuarial de referencia que contiene el modelo actual.")

    with col2:
        edad_actual = st.number_input("Edad actual", min_value=18, max_value=64, value=40, step=1, help="Edad en años cumplidos. El modelo estima el horizonte hasta la edad de pensión seleccionada.")
        edad_pension = st.radio(
            "¿A qué edad deseas pensionarte?",
            [60, 65],
            horizontal=True,
            help="El Fondo de Pensiones para el Bienestar solo aplica a los 65 años. Si eliges 60, se calculará la pensión por Cesantía sin ese complemento."
        )
        if edad_pension == 60:
            st.warning("⚠️ A los 60 años NO aplica el Complemento del Fondo del Bienestar. Solo se calcula la pensión por Cesantía con tu saldo de AFORE.")
        else:
            st.success("✅ A los 65 años aplica el Complemento del Fondo del Bienestar (con tope).")

    # ==========================================
    # PASO 2: DATOS FINANCIEROS
    # ==========================================
    st.markdown("---")
    st.markdown("### 💰 Paso 2: Tus Datos Financieros")
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
    st.markdown("### 🏥 Paso 3: Tu Perfil Laboral")
    es_empleado_imss = st.checkbox("¿Eres trabajador de base del propio IMSS, contratado después del 1 de agosto de 2008?", help="Marca esta opción únicamente si eres personal de base del Instituto Mexicano del Seguro Social y aplica la retención descrita abajo.")

    porcentaje_ahorro_imss = 0.11 if es_empleado_imss else 0.0
    saldo_voluntario_actual = 0.0

    if es_empleado_imss:
        st.markdown("""
        <div class="info-box">
        <strong>📌 Nota:</strong> Como empleado del IMSS, tienes una retención automática del 11% para tu ahorro voluntario (tarjetón) conforme al Contrato Colectivo.
        </div>
        """, unsafe_allow_html=True)
        saldo_voluntario_actual = st.number_input("Saldo actual del ahorro por tarjetón / ahorro voluntario (MXN)", min_value=0.0, value=0.0, step=5000.0, format="%.2f", help="Captura el saldo acumulado que corresponda a este ahorro, según el estado de cuenta disponible. Si no lo conoces, solicita confirmación antes de usar el resultado como definitivo.")
        if saldo_voluntario_actual > 0:
            st.caption(f"**${saldo_voluntario_actual:,.2f} MXN**")

    # ==========================================
    # PASO 4: ESTRATEGIA FISCAL
    # ==========================================
    st.markdown("---")
    st.markdown("### ⚖️ Paso 4: Tu Estrategia Fiscal")
    quiere_deducir = st.radio(
        "¿Qué enfoque fiscal te interesa explorar?",
        ["Sí, quiero deducir y buscar devoluciones del SAT cada año",
         "No, prefiero no deducir hoy y exentar de impuestos mi dinero al final"],
        help="Es una preferencia inicial para mostrar una estimación ilustrativa. La procedencia del tratamiento fiscal depende del producto, los requisitos legales y tu situación particular; debe validarse antes de tomar decisiones."
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
    if st.button("🚀 Calcular mi Diagnóstico de Retiro"):
        if fecha_primera_cotizacion is None:
            st.error("Selecciona la fecha de tu primera cotización registrada ante el IMSS para validar el régimen antes de calcular.")
        elif fecha_primera_cotizacion < date(1997, 7, 1):
            st.error("Cálculo bloqueado: la fecha capturada corresponde a una posible situación de Ley 73 / transición. No se generará un diagnóstico Ley 97 con estos datos.")
        elif salario_mensual == 0:
            st.error("Por favor, ingresa tu sueldo mensual actual.")
        else:
            with st.spinner("Calculando tu diagnóstico..."):
                anos_futuros = edad_pension - edad_actual
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

                ae_fija = ANUALIDADES[sexo][edad_pension]
                pension_base = (saldo_afore_acumulado / ((1 + MARGEN_SEGURIDAD) * ae_fija)) * FACTOR_PENSION_97 / 12

                if edad_pension == 65 and pension_base < TOPE_BIENESTAR:
                    complemento_solidario = max(0.0, TOPE_BIENESTAR - pension_base)
                else:
                    complemento_solidario = 0.0

                pension_obligatoria_total = pension_base + complemento_solidario

                saldo_voluntario_acumulado = saldo_voluntario_actual
                for mes in range(1, meses_totales + 1):
                    aportacion_voluntaria_tarjeton = salario_mensual * porcentaje_ahorro_imss
                    saldo_voluntario_acumulado = (saldo_voluntario_acumulado * (1 + tasa_mensual_neta_afore)) + aportacion_voluntaria_tarjeton

                pension_generada_voluntario = (saldo_voluntario_acumulado / ((1 + MARGEN_SEGURIDAD) * ae_fija)) * FACTOR_PENSION_97 / 12

                pension_afore_consolidada = pension_obligatoria_total + pension_generada_voluntario
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
                st.markdown(f"## 📊 Tu Diagnóstico de Retiro a los {edad_pension} años")

                col_a, col_b, col_c = st.columns([1, 1, 1])
                with col_a:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Pensión Estimada</h3>
                        <div class="value">${pension_obligatoria_total:,.0f}</div>
                        <div class="label">MXN mensuales</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Tasa de Reemplazo</h3>
                        <div class="value">{tasa_reemplazo:.1f}%</div>
                        <div class="label">de tu sueldo actual</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Brecha Mensual</h3>
                        <div class="value">${brecha_patrimonial:,.0f}</div>
                        <div class="label">MXN por cubrir</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Sección 1
                st.markdown("---")
                st.markdown("### 📊 1. Diagnóstico del Sistema Obligatorio (Afore)")
                st.write(f"- Fondo estimado acumulado por Ley: **${saldo_afore_acumulado:,.2f} MXN**")
                st.write(f"- Pensión base a los {edad_pension} años: **${pension_base:,.2f} MXN**")
                if edad_pension == 65 and complemento_solidario > 0:
                    st.write(f"- Complemento del Bienestar: **${complemento_solidario:,.2f} MXN**")
                if edad_pension == 60:
                    st.write(f"- Complemento del Bienestar: **No aplica a los 60 años**")
                st.write(f"- **Pensión Mensual Obligatoria Protegida: ${pension_obligatoria_total:,.2f} MXN**")

                # Sección 2 (solo si es IMSS)
                if es_empleado_imss:
                    st.markdown("---")
                    st.markdown("### 🏦 2. Rendimiento de tu Ahorro Voluntario Actual")
                    st.write(f"- Aportación mensual estimada (11% del sueldo): **${salario_mensual * porcentaje_ahorro_imss:,.2f} MXN**")
                    st.write(f"- Saldo inicial de ahorro voluntario: **${saldo_voluntario_actual:,.2f} MXN**")
                    st.write(f"- Años de proyección: **{anos_futuros} años**")
                    st.write(f"- Rendimiento anual aplicado: **{RENDIMIENTO_ANUAL_AFORE*100:.2f}%**")
                    st.write(f"- **Fondo total estimado de Ahorro Voluntario a los {edad_pension} años: ${saldo_voluntario_acumulado:,.2f} MXN**")
                    st.write(f"- **Pensión mensual extra generada por tu Ahorro Voluntario: ${pension_generada_voluntario:,.2f} MXN**")

                # Sección 3
                st.markdown("---")
                st.markdown("### 🚨 3. Análisis de la Brecha en tu Estilo de Vida")

                if es_empleado_imss:
                    st.write(f"Hoy ganas **${salario_mensual:,.2f} MXN**, pero sumando tu Afore Obligatoria y tu Ahorro Voluntario solo cubres el **{tasa_reemplazo:.1f}%** de tus ingresos.")
                else:
                    st.write(f"Hoy ganas **${salario_mensual:,.2f} MXN**, pero tu Afore Obligatoria solo cubre el **{tasa_reemplazo:.1f}%** de tus ingresos.")

                if brecha_patrimonial > 0:
                    st.markdown(f"""
                    <div class="warning-box">
                    <strong>Te harán falta cada mes: ${brecha_patrimonial:,.2f} MXN.</strong><br>
                    Este es el bache que debes cubrir para mantener tu estilo de vida.
                    </div>
                    """, unsafe_allow_html=True)

                    # Sección 4
                    st.markdown("---")
                    st.markdown("### 📈 4. Plan de Ahorro Privado Sugerido")
                    capital_necesario_comp = (brecha_patrimonial * 12 * ae_fija * (1 + MARGEN_SEGURIDAD)) / FACTOR_PENSION_97

                    if meses_totales > 0:
                        factor_acumulacion = ((1 + tasa_mensual_comp) ** meses_totales - 1) / tasa_mensual_comp
                        aportacion_requerida = capital_necesario_comp / factor_acumulacion
                    else:
                        aportacion_requerida = 0.0

                    aportacion_final_comp = max(MINIMO_APORTACION, aportacion_requerida)
                    pension_generada_ahorro = (capital_necesario_comp * FACTOR_PENSION_97) / (ae_fija * (1 + MARGEN_SEGURIDAD)) / 12

                    st.write(f"- **Fondo de Reserva Privado a Construir: ${capital_necesario_comp:,.2f} MXN**")
                    st.metric(label="Ahorro Mensual Sugerido", value=f"${aportacion_final_comp:,.2f} MXN")

                    # Sección 5
                    st.markdown("---")
                    st.markdown("### 🏢 5. Resumen Consolidado de tu Pensión Mensual Futura")
                    pension_consolidada_final = pension_obligatoria_total + pension_generada_voluntario + pension_generada_ahorro

                    st.markdown(f"""
                    <div class="success-box">
                    <strong>💰 INGRESO MENSUAL TOTAL ESTIMADO AL RETIRO:</strong><br>
                    <span style="font-size: 2rem; font-weight: 700; color: #1e3a5f;">${pension_consolidada_final:,.2f} MXN</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write(f"• (+) Pensión por tu Afore Obligatoria de Ley: **${pension_obligatoria_total:,.2f} MXN**")
                    if es_empleado_imss:
                        st.write(f"• (+) Pensión extra por tu Ahorro Voluntario IMSS: **${pension_generada_voluntario:,.2f} MXN**")
                    st.write(f"• (+) Pensión estimada por tu Plan Privado Sugerido: **${pension_generada_ahorro:,.2f} MXN**")

                    # Sección 6
                    if "Sí, quiero deducir" in quiere_deducir:
                        st.markdown("---")
                        st.markdown("### 💵 6. Estimación de Recuperación de Impuestos")
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
                        st.metric(label="Saldo a favor estimado en tu Declaración Anual", value=devolucion_texto_reporte)
                        st.write(f"Costo mensual neto real de tu ahorro: **${(aportacion_final_comp - (devolucion_estimada/12)):,.2f} MXN**")
                    else:
                        st.markdown("---")
                        st.markdown("### 🛡️ 6. Beneficio de Exención de Impuestos (Artículo 93)")
                        st.write("• Al no deducir hoy, tu dinero se entrega **100% libre de impuestos** al retirarlo a los 60 años con 5 años de vigencia.")

                else:
                    st.success("🎉 Según los datos capturados, tu Afore cubre tu sueldo actual.")
                    pension_consolidada_final = pension_obligatoria_total + pension_generada_voluntario

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
                pdf.cell(0, 6, f"Sexo: {sexo} | Edad actual: {edad_actual} anos", ln=True)
                pdf.cell(0, 6, f"Edad de pension seleccionada: {edad_pension} anos", ln=True)
                pdf.cell(0, 6, f"Primera cotizacion IMSS capturada: {fecha_primera_cotizacion.strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 6, "Regimen evaluado por fecha capturada: Ley 97 (validar con constancia oficial)", ln=True)
                pdf.cell(0, 6, f"Sueldo Mensual Bruto: {salario_mensual:,.2f} MXN", ln=True)
                pdf.ln(5)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "2. DIAGNOSTICO DEL SISTEMA OBLIGATORIO (AFORE)", ln=True)
                pdf.set_font("Helvetica", size=11)
                pdf.cell(0, 6, f"Fondo estimado acumulado: {saldo_afore_acumulado:,.2f} MXN", ln=True)
                pdf.cell(0, 6, f"Pension base a los {edad_pension} anos: {pension_base:,.2f} MXN", ln=True)
                if edad_pension == 65 and complemento_solidario > 0:
                    pdf.cell(0, 6, f"Complemento del Bienestar: {complemento_solidario:,.2f} MXN", ln=True)
                if edad_pension == 60:
                    pdf.cell(0, 6, "Complemento del Bienestar: No aplica a los 60 anos", ln=True)
                pdf.cell(0, 6, f"Pension Mensual Obligatoria: {pension_obligatoria_total:,.2f} MXN", ln=True)
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
                pdf.cell(0, 6, f"(+) Afore Obligatoria: {pension_obligatoria_total:,.2f} MXN", ln=True)
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
                pdf.multi_cell(0, 5, "AVISO: Los resultados son estimaciones hipoteticas con fines ilustrativos. No representan una cantidad garantizada ni una resolucion oficial del IMSS.")

                pdf_output = bytes(pdf.output())
                st.download_button(
                    label="📥 Descargar Diagnóstico Patrimonial en PDF",
                    data=bytes(pdf_output),
                    file_name=f"Plan_Retiro_{re.sub(r'[^A-Za-z0-9_-]+', '_', str(fecha_primera_cotizacion)).strip('_') or 'Prospecto'}.pdf",
                    mime="application/pdf"
                )

                st.markdown("---")
                st.caption("AVISO: los resultados son estimaciones hipotéticas y no tienen valor oficial. No garantizan el monto de una pensión ni sustituyen la validación de semanas, salario base, régimen y requisitos ante el IMSS/AFORE.")
else:
    st.info("Para comenzar, consulta el Aviso de Privacidad y marca la casilla de autorización. No se mostrarán los campos de captura hasta que lo hagas.")
