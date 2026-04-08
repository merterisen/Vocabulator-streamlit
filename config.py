# Central place for constants. s

WINDOW_TITLE = "Vocabulator"

# NLP Configuration
LANGUAGES = {
    "German": {
        "model": "de_core_news_sm",
        "articles": {"Masc": "der", "Fem": "die", "Neut": "das"},
        "abb": "de",
    },
    "English": {
        "model": "en_core_web_sm",
        "articles": {},
        "abb": "en",
    },
    "French": {
        "model": "fr_core_news_sm",
        "articles": {"Masc": "le", "Fem": "la"},
        "abb": "fr",
    },
    "Spanish": {
        "model": "es_core_news_sm",
        "articles": {"Masc": "el", "Fem": "la"},
        "abb": "es",
    },
}

VALID_POS_TAGS = {"NOUN", "VERB", "ADJ", "ADV"}


# LLM Configuration
LLM_BATCH_SIZE = 20

# OpenAI Prices per 1M tokens.
# https://developers.openai.com/api/docs/pricing

LLM_MODELS = {
    # OPENAI
    "gpt-5.4": {"model": "gpt-5.4", "type": "openai", "input_price": 2.50, "output_price": 15.00},
    "gpt-5.4-mini": {"model": "gpt-5.4-mini", "type": "openai", "input_price": 0.75, "output_price": 4.00},
    "gpt-5.4-nano": {"model": "gpt-5.4-nano", "type": "openai", "input_price": 0.20, "output_price": 1.25},
    "gpt-5.1": {"model": "gpt-5.1", "type": "openai", "input_price": 1.25, "output_price": 10.00},
}
