import pandas as pd
import genanki
import tempfile
import os
import hashlib
import random

class AnkiManager:
    def __init__(self, deck_name="Vocabulator Deck"):
        self.deck_name = deck_name
        self.model_id = 2602382488 # Hardcoded unique ID for the model

        # Use hash of the deck name for the deck ID to separate decks from overwriting each other in Anki
        #hash_str = hashlib.sha256(self.deck_name.encode('utf-8')).hexdigest()
        #self.deck_id = int(hash_str, 16) % (1 << 31)
        
        # Use a random ID for each deck to ensure they are created as new decks in Anki
        self.deck_id = random.randrange(1 << 30, 1 << 31)

        self.model = genanki.Model(
            model_id=self.model_id,
            name='Vocabulator Note Type',
            
            fields=[
                {'name': 'word'},
                {'name': 'sentence'},
                {'name': 'audio'},
                {'name': 'translate_word'},
                {'name': 'translate_sentence'},
                {'name': 'translate_note'},
            ],

            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': """
                            {{word}}
                            {{#sentence}}
                            <br><br>
                            <i>{{sentence}}</i>
                            {{/sentence}}
                            {{audio}}
                            """,

                    'afmt': """
                            {{FrontSide}}
                            <hr id=answer>
                            {{translate_word}}
                            {{#translate_sentence}}
                            <br><br>
                            <i>{{translate_sentence}}</i>
                            {{/translate_sentence}}
                            {{#translate_note}}
                            <br><br>
                            <small>{{translate_note}}</small>
                            {{/translate_note}}
                            """,
                },
                {
                    'name': 'Card 2',
                    'qfmt': """
                            {{translate_word}}
                            {{#translate_sentence}}
                            <br><br>
                            <i>{{translate_sentence}}</i>
                            {{/translate_sentence}}
                            {{#translate_note}}
                            <br><br>
                            <small>{{translate_note}}</small>
                            {{/translate_note}}
                            """,
                    'afmt': """
                            {{FrontSide}}
                            <hr id=answer>
                            {{word}}
                            {{#sentence}}
                            <br><br>
                            <i>{{sentence}}</i>
                            {{/sentence}}
                            {{audio}}
                            """,
                },
            ],

            css=
                """
                .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
                }
                """
        )

    def generate_apkg(self, df: pd.DataFrame) -> bytes:
        deck = genanki.Deck(
            self.deck_id,
            self.deck_name
        )

        for _, row in df.iterrows():
            word = str(row.get('word', '')) if not pd.isna(row.get('word')) else ''
            sentence = str(row.get('sentence', '')) if 'sentence' in row and not pd.isna(row.get('sentence')) else ''
            audio = ''
            translate_word = str(row.get('translate_word', '')) if 'translate_word' in row and not pd.isna(row.get('translate_word')) else ''
            translate_sentence = str(row.get('translate_sentence', '')) if 'translate_sentence' in row and not pd.isna(row.get('translate_sentence')) else ''
            translate_note = ''

            note = genanki.Note(
                model=self.model,
                fields=[word, sentence, audio, translate_word, translate_sentence, translate_note]
            )
            deck.add_note(note)

        package = genanki.Package(deck)
        
        fd, temp_path = tempfile.mkstemp(suffix='.apkg')
        os.close(fd)
        
        try:
            package.write_to_file(temp_path)
            with open(temp_path, 'rb') as f:
                data = f.read()
        finally:
            os.remove(temp_path)
            
        return data
