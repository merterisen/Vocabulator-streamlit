import math
import concurrent.futures
from openai import OpenAI
import pandas as pd
from typing import List
from pydantic import BaseModel, Field
from config import LLM_BATCH_SIZE, LLM_MODELS

class TranslationItem(BaseModel):
    word: str = Field(description="The original word")
    sentence: str = Field(description="Example sentence in source language")
    translate_word: str = Field(description="Translated word")
    translate_sentence: str = Field(description="Translated sentence")

class TranslationResponse(BaseModel):
    items: List[TranslationItem] = Field(description="List of translations for the requested words")

class LLMManager:
    """
    Responsible for connecting to LLM providers and adding new columns:
        - sentence
        - translate_word
        - translate_sentence
    """

    def __init__(self, llm_model, api_key, llm_workers):
        self.llm_model = llm_model
        self.client = OpenAI(api_key=api_key)
        self.llm_workers = llm_workers
    

    # =================================================================
    # GLOBAL FUNCTIONS
    # =================================================================

    def create_translates(self, input_df:pd.DataFrame, language:str, translate_language:str, exclude_known_words_llm:bool) -> pd.DataFrame:
        if input_df is None or input_df.empty:
            return input_df

        if exclude_known_words_llm:
            words = input_df[input_df['is_known'] == False]['word'].tolist()
        else:
            words = input_df['word'].tolist()
        batch_size = LLM_BATCH_SIZE
        total_batches = math.ceil(len(words) / batch_size)        
        output_data = {}

        batches = [words[i*batch_size : (i+1)*batch_size] for i in range(total_batches)]

        def process_batch(batch_idx, words_to_send_llm):
            try:
                client_output = self._send_to_llm(words_to_send_llm, language, translate_language)
                return batch_idx, words_to_send_llm, client_output, None
            except Exception as e:
                return batch_idx, words_to_send_llm, None, e

        # Using parallel workers to speed up without hitting rate limits too quickly
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.llm_workers) as executor:
            futures = [executor.submit(process_batch, i, batch) for i, batch in enumerate(batches)]
            for future in concurrent.futures.as_completed(futures):
                batch_idx, words_to_send_llm, client_output, error = future.result()
                if error:
                    print(f"Error processing batch {batch_idx} for words {words_to_send_llm}: {error}")
                elif client_output:
                    for item in client_output:
                        word_key = item.get("word", "").lower().strip()
                        if word_key:
                            output_data[word_key] = item
        

        # Using apply to safely map, if a word failed -> leave fields empty
        output_df = input_df.copy()
        output_df['sentence'] = output_df['word'].apply(lambda x: output_data.get(x.lower().strip(), {}).get('sentence', ''))
        output_df['translate_word'] = output_df['word'].apply(lambda x: output_data.get(x.lower().strip(), {}).get('translate_word', ''))
        output_df['translate_sentence'] = output_df['word'].apply(lambda x: output_data.get(x.lower().strip(), {}).get('translate_sentence', ''))
        
        return output_df
                

    def estimate_cost(self, input_df: pd.DataFrame, exclude_known_words_llm: bool) -> str:
        """
        Estimate the cost of processing the input_df with the current LLM model.
        Returns a formatted string with token count and estimated cost.
        """

        if exclude_known_words_llm:
            words = input_df[input_df['is_known'] == False]['word'].tolist()
        else:
            words = input_df['word'].tolist()
        
        total_words = len(words)
        batch_size = LLM_BATCH_SIZE
        num_batches = math.ceil(total_words / batch_size)

        # Heuristic Estimation
        fixed_prompt_overhead = 250
        per_word_input_tokens = 5

        input_tokens = (num_batches * fixed_prompt_overhead) + (total_words * per_word_input_tokens)
        output_tokens = total_words * 80  # ~80 tokens per word (JSON Structure + Sentence + Translation)

        llm_model_config = LLM_MODELS.get(self.llm_model)
        if not llm_model_config:
            return f"Model {self.llm_model} not found in config. Cannot estimate cost."

        input_price_per_1m = llm_model_config.get("input_price", 0)
        output_price_per_1m = llm_model_config.get("output_price", 0)

        estimated_cost = (input_tokens / 1_000_000 * input_price_per_1m) + (output_tokens / 1_000_000 * output_price_per_1m)

        if estimated_cost < 0.01:
            estimated_cost_text = "< $0.01"
        else:
            estimated_cost_text = f"~${estimated_cost:.2f}"
        
        total_tokens = input_tokens + output_tokens
        return f"You are about to process ~{total_tokens} tokens using {self.llm_model}.\n\nEstimated Cost: {estimated_cost_text} USD\n"


    # =================================================================
    # LOCAL FUNCTIONS
    # =================================================================

    def _send_to_llm(self, words_to_send_llm:list, language:str, translate_language:str) -> list:

        prompt = f"""
        You are a vocabulary assistant.
        Source Language: {language}
        Target Language: {translate_language}
        
        Word List: {", ".join(words_to_send_llm)}

        Task:
        For each word in the list, provide:
        1. An example sentence in the Source Language ({language}) containing the word.
        2. The translation of the word in the Target Language ({translate_language}).
        3. The translation of the example sentence in the Target Language ({translate_language}).
        """

        response = self.client.beta.chat.completions.parse(
            model = self.llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful dictionary assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=TranslationResponse,
        )

        parsed_response = response.choices[0].message.parsed
        if parsed_response:
            return [item.model_dump() for item in parsed_response.items]
        return []