# Mapping for 21 classes of Polish traffic signs dataset
# The folders are loaded alphabetically by Keras: A1, A17, A2, A21...
SIGN_MAPPING = {
    0: "A-1 (Niebezpieczny zakręt w prawo)",
    1: "A-17 (Dzieci)",
    2: "A-2 (Niebezpieczny zakręt w lewo)",
    3: "A-21 (Tramwaj)",
    4: "A-30 (Inne niebezpieczeństwo)",
    5: "A-7 (Ustąp pierwszeństwa)",
    6: "B-1 (Zakaz ruchu w obu kierunkach)",
    7: "B-2 (Zakaz wjazdu)",
    8: "B-20 (Stop)",
    9: "B-21 (Zakaz skręcania w lewo)",
    10: "B-22 (Zakaz skręcania w prawo)",
    11: "B-23 (Zakaz zawracania)",
    12: "B-33 (Ograniczenie prędkości)",
    13: "B-36 (Zakaz zatrzymywania się)",
    14: "B-41 (Zakaz ruchu pieszych)",
    15: "C-12 (Ruch okrężny)",
    16: "C-2 (Nakaz jazdy w prawo za znakiem)",
    17: "C-4 (Nakaz jazdy w lewo za znakiem)",
    18: "D-1 (Droga z pierwszeństwem)",
    19: "D-6 (Przejście dla pieszych)",
    20: "Inne znaki (other)"
}

NUM_CLASSES = len(SIGN_MAPPING)

def get_sign_name(class_id):
    """Returns the human-readable name of the sign."""
    return SIGN_MAPPING.get(class_id, "Nieznany znak")
