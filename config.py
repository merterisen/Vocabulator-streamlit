# Central place for constants. s

WINDOW_TITLE = "Vocabulator"

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

# NLP Configuration
LANGUAGES = {
    "Catalan": {
        "model": "ca_core_news_sm",
        "articles": {"Masc": "el", "Fem": "la"}
    },
    "Chinese": {
        "model": "zh_core_web_sm",
        "articles": {}
    },
    "Croatian": {
        "model": "hr_core_news_sm",
        "articles": {}
    },
    "Danish": {
        "model": "da_core_news_sm",
        "articles": {"Com": "den", "Neut": "det"}
    },
    "Dutch": {
        "model": "nl_core_news_sm",
        "articles": {"Com": "de", "Neut": "het"}
    },
    "English": {
        "model": "en_core_web_sm",
        "articles": {},
    },
    "Finnish": {
        "model": "fi_core_news_sm",
        "articles": {},
    },
    "French": {
        "model": "fr_core_news_sm",
        "articles": {"Masc": "le", "Fem": "la"},
    },
    "German": {
        "model": "de_core_news_sm",
        "articles": {"Masc": "der", "Fem": "die", "Neut": "das"},
    },
    "Greek": {
        "model": "el_core_news_sm",
        "articles": {"Masc": "o", "Fem": "η", "Neut": "το"},
    },
    "Italian": {
        "model": "it_core_news_sm",
        "articles": {"Masc": "il", "Fem": "la"},
    },
    "Japanese": {
        "model": "ja_core_news_sm",
        "articles": {},
    },
    "Korean": {
        "model": "ko_core_news_sm",
        "articles": {},
    },
    "Lithuanian": {
        "model": "lt_core_news_sm",
        "articles": {},
    },
    "Macedonian": {
        "model": "mk_core_news_sm",
        "articles": {},
    },
    "Multi-language": {
        "model": "xx_ent_wiki_sm",
        "articles": {},
    },
    "Norwegian Bokmål": {
        "model": "nb_core_news_sm",
        "articles": {"Masc": "den", "Fem": "den", "Neut": "det"},
    },
    "Polish": {
        "model": "pl_core_news_sm",
        "articles": {},
    },
    "Portuguese": {
        "model": "pt_core_news_sm",
        "articles": {"Masc": "o", "Fem": "a"},
    },
    "Romanian": {
        "model": "ro_core_news_sm",
        "articles": {},
    },
    "Russian": {
        "model": "ru_core_news_sm",
        "articles": {},
    },
    "Slovenian": {
        "model": "sl_core_news_sm",
        "articles": {},
    },
    "Spanish": {
        "model": "es_core_news_sm",
        "articles": {"Masc": "el", "Fem": "la"},
    },
    "Swedish": {
        "model": "sv_core_news_sm",
        "articles": {"Com": "den", "Neut": "det"},
    },
    "Ukrainian": {
        "model": "uk_core_news_sm",
        "articles": {},
    },
}

VALID_POS_TAGS = {"NOUN", "VERB", "ADJ", "ADV"}