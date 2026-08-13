import streamlit as st


def inicializar_estado(play_key, idx_key):
    """
    Inicializa el estado del reproductor.
    """

    if play_key not in st.session_state:
        st.session_state[play_key] = False

    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0


def dibujar_reproductor(
    periodos,
    play_key,
    idx_key,
    slider_key,
    formato="%Y-%m",
    velocidad=0.6
):
    """
    Reproductor temporal basado en st.fragment.

    Comportamiento:
    - ► inicia la reproducción.
    - ❚❚ pausa.
    - El slider permite seleccionar manualmente un período.
    - La reproducción termina en el último período.
    - Si se pulsa ► estando en el último período,
      vuelve al primer período.
    """

    if not periodos:
        return

    # --------------------------------------------------
    # 1. Inicializar estado
    # --------------------------------------------------

    inicializar_estado(
        play_key,
        idx_key
    )

    # --------------------------------------------------
    # 2. Determinar frecuencia del fragmento
    # --------------------------------------------------

    run_every = (
        velocidad
        if st.session_state[play_key]
        else None
    )

    # --------------------------------------------------
    # 3. Fragmento del reproductor
    # --------------------------------------------------

    @st.fragment(run_every=run_every)
    def reproductor():

        # ----------------------------------------------
        # Avance automático
        # ----------------------------------------------

        if st.session_state[play_key]:

            if st.session_state[idx_key] < len(periodos) - 1:

                st.session_state[idx_key] += 1

            else:

                # Llegamos al último período
                st.session_state[play_key] = False

        # ----------------------------------------------
        # Controles
        # ----------------------------------------------

        c_play, c_slider = st.columns(
            [0.7, 11.3],
            vertical_alignment="center"
        )

        # ----------------------------------------------
        # Botón Play / Pausa
        # ----------------------------------------------

        with c_play:

            etiqueta = (
                "❚❚"
                if st.session_state[play_key]
                else "►"
            )

            if st.button(
                etiqueta,
                key=f"btn_{play_key}",
                use_container_width=True
            ):

                if st.session_state[play_key]:

                    st.session_state[play_key] = False

                else:

                    if st.session_state[idx_key] >= len(periodos) - 1:
                        st.session_state[idx_key] = 0

                    st.session_state[play_key] = True

                st.rerun()

        # ----------------------------------------------
        # Slider
        # ----------------------------------------------

        with c_slider:

            periodo_seleccionado = st.select_slider(
                "Periodo",
                options=periodos,
                value=periodos[
                    st.session_state[idx_key]
                ],
                format_func=lambda x: x.strftime(formato),
                key=slider_key,
                label_visibility="collapsed"
            )

            nuevo_idx = periodos.index(
                periodo_seleccionado
            )

            if (
                nuevo_idx != st.session_state[idx_key]
                and not st.session_state[play_key]
            ):

                st.session_state[idx_key] = nuevo_idx

                st.rerun()

    # --------------------------------------------------
    # 4. Ejecutar reproductor
    # --------------------------------------------------

    reproductor()