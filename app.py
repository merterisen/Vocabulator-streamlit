import streamlit as st
import config
from managers.nlp_manager import NLPManager
from managers import pdf_manager
from managers.llm_manager import LLMManager
import io

st.set_page_config(page_title=config.WINDOW_TITLE, layout="wide")

# State Management: To prevent the DataFrame from being lost when the page is refreshed
if 'output_df' not in st.session_state:
    st.session_state['output_df'] = None

st.title(config.WINDOW_TITLE)

left_col, right_col = st.columns([1, 1.4], gap="large")

with left_col:
    with st.container():
        nlp_tab, llm_tab, editor_tab = st.tabs(["NLP", "LLM", "DATA"])

        # ==========================================
        # NLP TAB
        # ==========================================
        with nlp_tab:
            st.subheader("1. Select PDF")
            uploaded_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")


            st.subheader("2. Select Language")
            language = st.selectbox("Language", list(config.LANGUAGES.keys()), label_visibility="collapsed")
            include_articles = st.checkbox("Include Articles")


            st.subheader("3. Select Known Words (Optional)")
            uploaded_known_words = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"], label_visibility="collapsed")


            if st.button("RUN NLP", type="primary"):
                if not uploaded_pdf:
                    st.error("Please select a PDF file.")
                else:
                    with st.spinner("Processing NLP..."):
                        try:
                            nlp_manager = NLPManager(language)
                            nlp_manager.load_model()
                            known_words = nlp_manager.load_known_words(uploaded_known_words) if uploaded_known_words else set()

                            texts = pdf_manager.extract_texts_from_pdf(uploaded_pdf)

                            st.session_state['output_df'] = nlp_manager.extract_words(texts, known_words, include_articles=include_articles)
                            st.success("NLP Complete!")
                        except Exception as e:
                            st.error(f"Process Error: {str(e)}")

        # ==========================================
        # LLM TAB
        # ==========================================
        with llm_tab:
            st.subheader("1. Select LLM Model")
            llm_model = st.selectbox("LLM Model", list(config.LLM_MODELS.keys()), label_visibility="collapsed")


            st.subheader("2. Enter Translate Language")
            translate_language = st.text_input('Language', value='English', placeholder='Enter Translate Language', label_visibility="collapsed")


            st.subheader("3. Enter API Key")
            api_key = st.text_input("API Key", type="password", label_visibility="collapsed")


            if st.button("RUN LLM", type="primary"):
                if st.session_state['output_df'] is None or st.session_state['output_df'].empty:
                    st.error("No words found. Please run NLP first.")
                elif not translate_language:
                    st.error("Please enter a translation language.")
                elif not api_key:
                    st.error("Please enter an API Key.")
                else:
                    with st.spinner("Processing LLM..."):
                        try:
                            llm_manager = LLMManager(llm_model, api_key)
                            st.session_state['output_df'] = llm_manager.create_translates(
                                st.session_state['output_df'], language, translate_language
                            )
                            st.success("LLM Complete!")
                        except Exception as e:
                            st.error(f"Process Error: {str(e)}")
        
        with editor_tab:
            threshold = st.number_input("Remove words with count <=", min_value=0, value=0)
            if st.button("Apply Threshold"):
                    st.session_state['output_df'] = st.session_state['output_df'][st.session_state['output_df']['count'] > threshold]
                    st.rerun()


         

with right_col:
    with st.container():

        if st.session_state['output_df'] is not None and not st.session_state['output_df'].empty:
            df = st.session_state['output_df']
            st.write(f"Total words: {len(df)}")

            st.session_state['output_df'] = st.data_editor(
                df,
                use_container_width=True,
                key="preview_editor",
                height=350
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                csv_data = st.session_state['output_df'].to_csv(index=False).encode('utf-8')
                st.download_button(label="Export CSV", data=csv_data, file_name="vocabulator_export.csv", mime="text/csv")

            with col2:
                buffer = io.BytesIO()
                st.session_state['output_df'].to_excel(buffer, index=False)
                st.download_button(label="Export Excel", data=buffer.getvalue(), file_name="vocabulator_export.xlsx", mime="application/vnd.ms-excel")
        else:
            st.title("Welcome to Vocabulator")

            st.markdown(
                """
            Vocabulator is an open-source word extraction tool that turns PDFs into focused vocabulary lists.

            - Extract words from your PDF files
            - Add AI translations and example sentences in your target language
            - Edit and export your final list in seconds
            - Built as an open-source project you can audit and contribute
            """
            )

            col1, col2 = st.columns(2)
            col1.metric("License", "Open Source")
            col2.metric("Export to", "CSV / Excel / Anki")