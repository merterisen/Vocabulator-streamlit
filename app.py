import streamlit as st
import config
from managers.nlp_manager import NLPManager
from managers.file_manager import FileManager
from managers.llm_manager import LLMManager
import io

st.set_page_config(page_title=config.WINDOW_TITLE, layout="wide")
file_manager = FileManager()

# State Management: persist dataframes across reruns
if 'source_df' not in st.session_state:
    st.session_state['source_df'] = None
if 'working_df' not in st.session_state:
    st.session_state['working_df'] = None

st.title(config.WINDOW_TITLE)

left_col, right_col = st.columns([1, 1.4], gap="large")

# ==========================================
# TABS
# ==========================================
with left_col:
    with st.container():
        nlp_tab, llm_tab, analyser_tab, settings_tab = st.tabs(["NLP", "LLM", "ANALYSER", "SETTINGS"])

        # ==========================================
        # NLP TAB
        # ==========================================
        with nlp_tab:
            st.subheader("1. Select File")
            uploaded_file = st.file_uploader("Upload File", label_visibility="collapsed")


            st.subheader("2. Select Language")
            language = st.selectbox("Language", list(config.LANGUAGES.keys()), index=8, label_visibility="collapsed")
            include_articles = st.checkbox("Include Articles")


            st.subheader("3. Select Known Words")
            st.caption("Optional: Upload a file containing the words you already know. This will mark those words when extracting vocabulary.")
            uploaded_known_words = st.file_uploader("Known Words", label_visibility="collapsed")


            if st.button("RUN NLP", type="primary"):
                if not uploaded_file:
                    st.error("Please select a file.")
                else:
                    known_words = set()
                    with st.spinner("Processing NLP..."):
                        try:
                            nlp_manager = NLPManager(language)
                            nlp_manager.load_model()

                            known_words_texts = (
                                file_manager.extract_texts_from_pdf(uploaded_known_words)
                                if uploaded_known_words
                                else []
                            )
                            known_words = nlp_manager.parse_known_words(known_words_texts)

                            texts = file_manager.extract_texts_from_pdf(uploaded_file)

                            source_df = nlp_manager.extract_words(
                                texts, known_words, include_articles=include_articles
                            )
                            # Immutable source data from NLP output.
                            st.session_state['source_df'] = source_df.copy(deep=True)
                            # Editable/transformable data for preview and user actions.
                            st.session_state['working_df'] = source_df.copy(deep=True)
                            st.success("NLP Complete!")
                        except Exception as e:
                            st.error(f"Process Error: {str(e)}")

        # ==========================================
        # LLM TAB
        # ==========================================
        with llm_tab:
            st.subheader("1. Select LLM Model")
            llm_model = st.selectbox("LLM Model", list(config.LLM_MODELS.keys()), index=2, label_visibility="collapsed")


            st.subheader("2. Enter Translate Language")
            translate_language = st.text_input('Language', value='English', placeholder='Enter Translate Language', label_visibility="collapsed")


            st.subheader("3. Enter API Key")
            api_key = st.text_input("API Key", type="password", label_visibility="collapsed")


            exclude_known_words = st.checkbox(
                "Exclude Known Words",
                value=True,
                help="Exclude words you already know from being sent to the LLM, to reduce token usage and API cost.",
            )


            if st.button("RUN LLM", type="primary"):
                if st.session_state['working_df'] is None or st.session_state['working_df'].empty:
                    st.error("No words found. Please run NLP first.")
                elif not translate_language:
                    st.error("Please enter a translation language.")
                elif not api_key:
                    st.error("Please enter an API Key.")
                else:
                    with st.spinner("Processing LLM..."):
                        try:
                            llm_manager = LLMManager(llm_model, api_key)
                            st.session_state['working_df'] = llm_manager.create_translates(
                                st.session_state['working_df'], language, translate_language
                            )
                            st.success("LLM Complete!")
                        except Exception as e:
                            st.error(f"Process Error: {str(e)}")

        # ==========================================
        # ANALYSER TAB
        # ==========================================
        with analyser_tab:
            if st.session_state['source_df'] is None or st.session_state['source_df'].empty:
                st.info("No analysis data yet. Run NLP first.")
            else:
                analysis_df = (
                    st.session_state['source_df']
                    .groupby("count")
                    .size()
                    .reset_index(name="unique_words")
                    .sort_values("count", ascending=False)
                )
                # Token coverage: each frequency bucket is weighted by count * unique_words.
                analysis_df["tokens"] = analysis_df["count"] * analysis_df["unique_words"]
                total_tokens = analysis_df["tokens"].sum()

                analysis_df["Percentage"] = analysis_df["tokens"] / total_tokens
                analysis_df["Cum. Percentage"] = analysis_df["Percentage"].cumsum()

                analysis_df["Percentage"] = analysis_df["Percentage"] * 100
                analysis_df["Cum. Percentage"] = analysis_df["Cum. Percentage"] * 100

                analysis_df = analysis_df.drop(columns=["tokens"])

                st.dataframe(
                    analysis_df,
                    hide_index=True,
                    column_config={
                        "Percentage": st.column_config.NumberColumn(format="%.2f"),
                        "Cum. Percentage": st.column_config.NumberColumn(format="%.2f"),
                    },
                )

        # ==========================================
        # SETTINGS TAB
        # ==========================================
        with settings_tab:
            threshold = st.number_input("Remove words with count smaller equal than <=", min_value=0, value=0)
            if st.button("Remove Words"):
                if st.session_state['working_df'] is None or st.session_state['working_df'].empty:
                    st.warning("No words found. Please run NLP first.")
                else:
                    st.session_state['working_df'] = st.session_state['working_df'][
                        st.session_state['working_df']['count'] > threshold
                    ]
                    st.rerun()

# ==========================================
# PREVIEW
# ==========================================
with right_col:
    with st.container():
        # If working DF is not empty
        if st.session_state['working_df'] is not None and not st.session_state['working_df'].empty:
            df = st.session_state['working_df']

            st.session_state['working_df'] = st.data_editor(
                df,
                key="preview_editor",
                height=350
            )

            st.write(f"Total words: {len(df)}")

            col1, col2 = st.columns([1, 1])

            with col1:
                csv_data = st.session_state['working_df'].to_csv(index=False).encode('utf-8')
                st.download_button(label="Export CSV", data=csv_data, file_name="vocabulator_export.csv", mime="text/csv")

            with col2:
                buffer = io.BytesIO()
                st.session_state['working_df'].to_excel(buffer, index=False)
                st.download_button(label="Export Excel", data=buffer.getvalue(), file_name="vocabulator_export.xlsx", mime="application/vnd.ms-excel")
        else:
            st.title("Welcome to Vocabulator")

            st.markdown(
                """
            Vocabulator is an open-source word extraction tool that turns files into focused vocabulary lists.

            - Extract words from your files
            - Add AI translations and example sentences in your target language
            - Edit and export your final list in seconds
            - Built as an open-source project you can audit and contribute
            """
            )

            col1, col2 = st.columns(2)
            col1.metric("Edition", "Open Source")
            col2.metric("Export to", "CSV / Excel / Anki")