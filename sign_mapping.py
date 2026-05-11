SIGN_MAPPING = {
    0: ("A-1", "Niebezpieczny zakręt w prawo"),
    1: ("A-11", "Nierówna droga"),
    2: ("A-11a", "Próg zwalniający"),
    3: ("A-12a", "Zwężenie jezdni - dwustronne"),
    4: ("A-14", "Roboty drogowe"),
    5: ("A-15", "Śliska jezdnia"),
    6: ("A-16", "Przejście dla pieszych"),
    7: ("A-17", "Dzieci"),
    8: ("A-18b", "Zwierzęta dzikie"),
    9: ("A-2", "Niebezpieczny zakręt w lewo"),
    10: ("A-20", "Odcinek jezdni o ruchu dwukierunkowym"),
    11: ("A-21", "Tramwaj"),
    12: ("A-24", "Rowerzyści"),
    13: ("A-29", "Sygnały świetlne"),
    14: ("A-3", "Niebezpieczne zakręty, pierwszy w prawo"),
    15: ("A-30", "Inne niebezpieczeństwo"),
    16: ("A-32", "Oszronienie jezdni"),
    17: ("A-4", "Niebezpieczne zakręty, pierwszy w lewo"),
    18: ("A-6a", "Skrzyżowanie z drogą podporządkowaną po obu stronach"),
    19: ("A-6b", "Skrzyżowanie z drogą podporządkowaną po prawej"),
    20: ("A-6c", "Skrzyżowanie z drogą podporządkowaną po lewej"),
    21: ("A-6d", "Wlot drogi jednokierunkowej z prawej"),
    22: ("A-6e", "Wlot drogi jednokierunkowej z lewej"),
    23: ("A-7", "Ustąp pierwszeństwa"),
    24: ("A-8", "Skrzyżowanie o ruchu okrężnym"),
    25: ("B-1", "Zakaz ruchu w obu kierunkach"),
    26: ("B-18", "Zakaz wjazdu pojazdów o masie ponad ... t."),
    27: ("B-2", "Zakaz wjazdu"),
    28: ("B-20", "STOP"),
    29: ("B-21", "Zakaz skręcania w lewo"),
    30: ("B-22", "Zakaz skręcania w prawo"),
    31: ("B-25", "Zakaz wyprzedzania"),
    32: ("B-26", "Zakaz wyprzedzania przez ciężarówki"),
    33: ("B-27", "Koniec zakazu wyprzedzania"),
    34: ("B-33", "Ograniczenie prędkości"),
    35: ("B-34", "Koniec ograniczenia prędkości"),
    36: ("B-36", "Zakaz zatrzymywania się"),
    37: ("B-41", "Zakaz ruchu pieszych"),
    38: ("B-42", "Koniec zakazów"),
    39: ("B-43", "Strefa ograniczonej prędkości"),
    40: ("B-44", "Koniec strefy ograniczonej prędkości"),
    41: ("B-5", "Zakaz wjazdu samochodów ciężarowych"),
    42: ("B-6-B-8-B-9", "Zakaz wjazdu pojazdów innych niż samochodowe"),
    43: ("B-8", "Zakaz wjazdu pojazdów zaprzęgowych"),
    44: ("B-9", "Zakaz wjazdu rowerów"),
    45: ("C-10", "Nakaz jazdy z lewej strony znaku"),
    46: ("C-12", "Ruch okrężny"),
    47: ("C-13", "Droga dla rowerów"),
    48: ("C-13-C-16", "Droga dla pieszych i rowerzystów"),
    49: ("C-13a", "Koniec drogi dla rowerów"),
    50: ("C-13a-C-16a", "Koniec drogi dla pieszych i rowerzystów"),
    51: ("C-16", "Droga dla pieszych"),
    52: ("C-2", "Nakaz jazdy w prawo za znakiem"),
    53: ("C-4", "Nakaz jazdy w lewo za znakiem"),
    54: ("C-5", "Nakaz jazdy prosto"),
    55: ("C-6", "Nakaz jazdy prosto lub w prawo"),
    56: ("C-7", "Nakaz jazdy prosto lub w lewo"),
    57: ("C-9", "Nakaz jazdy z prawej strony znaku"),
    58: ("D-1", "Droga z pierwszeństwem"),
    59: ("D-14", "Koniec pasa ruchu"),
    60: ("D-15", "Przystanek autobusowy"),
    61: ("D-18", "Parking"),
    62: ("D-18b", "Parking zadaszony"),
    63: ("D-2", "Koniec drogi z pierwszeństwem"),
    64: ("D-21", "Szpital"),
    65: ("D-23", "Stacja paliwowa"),
    66: ("D-23a", "Stacja z gazem do napędu pojazdów"),
    67: ("D-24", "Telefon"),
    68: ("D-26", "Stacja obsługi technicznej"),
    69: ("D-26b", "Myjnia"),
    70: ("D-26c", "Toaleta publiczna"),
    71: ("D-27", "Bufet lub kawiarnia"),
    72: ("D-28", "Restauracja"),
    73: ("D-29", "Hotel (motel)"),
    74: ("D-3", "Droga jednokierunkowa"),
    75: ("D-40", "Strefa zamieszkania"),
    76: ("D-41", "Koniec strefy zamieszkania"),
    77: ("D-42", "Obszar zabudowany"),
    78: ("D-43", "Koniec obszaru zabudowanego"),
    79: ("D-4a", "Droga bez przejazdu"),
    80: ("D-4b", "Wjazd na drogę bez przejazdu"),
    81: ("D-51", "Automatyczna kontrola prędkości"),
    82: ("D-52", "Strefa ruchu"),
    83: ("D-53", "Koniec strefy ruchu"),
    84: ("D-6", "Przejście dla pieszych"),
    85: ("D-6b", "Przejście dla pieszych i przejazd dla rowerów"),
    86: ("D-7", "Droga ekspresowa"),
    87: ("D-8", "Koniec drogi ekspresowej"),
    88: ("D-9", "Autostrada"),
    89: ("D-tablica", "Zbiorcza tablica informacyjna"),
    90: ("G-1a", "Słupek wskaźnikowy - trzy kreski po prawej stronie"),
    91: ("G-3", "Krzyż św. Andrzeja przed przejazdem kolejowym"),
}
NAZWA_DO_INDEX = {v[0]: k for k, v in SIGN_MAPPING.items()}


def get_sign_name(index):
    if index in SIGN_MAPPING:
        kod, nazwa = SIGN_MAPPING[index]
        return f"{kod} ({nazwa})"
    return "Nieznany znak"


def get_sign_code(index):
    if index in SIGN_MAPPING:
        kod, nazwa = SIGN_MAPPING[index]
        return kod
    return "Unknown"


def is_speed_limit(index):
    code = get_sign_code(index)
    return code in ["B-33", "B-43", "D-51"]


KLASY = sorted(SIGN_MAPPING.keys())
NUM_CLASSES = len(KLASY)
