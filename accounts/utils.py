SYNONYMS = {
    # =========================
    # نیا شناختی کارڈ
    # =========================
    "naya": "new",
    "nai": "new",
    "nayi": "new",
    "new": "new",
    "pehla": "new",
    "pehli": "new",
    "fresh": "new",
    "first": "new",

    # =========================
    # ب فارم
    # =========================
    "bform": "b_form",
    "b-form": "b_form",
    "b form": "b_form",
    "bay form": "b_form",
    "b فارم": "b_form",
    "child registration": "b_form",
    "crc": "b_form",

    # =========================
    # شناختی کارڈ تجدید
    # =========================
    "tajdeed": "renewal",
    "renew": "renewal",
    "renewal": "renewal",
    "expiry": "renewal",
    "expire": "renewal",
    "dobara banana": "renewal",
    "update expiry": "renewal",

    # =========================
    # گمشدہ شناختی کارڈ
    # =========================
    "gum": "lost",
    "gumshuda": "lost",
    "lost": "lost",
    "missing": "lost",
    "chori": "lost",
    "stolen": "lost",
    "card kho gaya": "lost",
    "id kho gaya": "lost",

    # =========================
    # فیملی رجسٹری سرٹیفکیٹ
    # =========================
    "family": "frc",
    "family certificate": "frc",
    "family registration": "frc",
    "frc": "frc",
    "family tree": "frc",

    # =========================
    # شادی اپڈیٹ
    # =========================
    "shadi": "marriage_update",
    "marriage": "marriage_update",
    "nikah": "marriage_update",
    "wife add": "marriage_update",
    "husband add": "marriage_update",
    "marital status": "marriage_update",

    # =========================
    # طلاق اپڈیٹ
    # =========================
    "talaq": "divorce_update",
    "divorce": "divorce_update",
    "separation": "divorce_update",
    "khula": "divorce_update",

    # =========================
    # پتہ تبدیلی
    # =========================
    "pata": "address_change",
    "address": "address_change",
    "address update": "address_change",
    "ghar change": "address_change",
    "location update": "address_change",
    "shift house": "address_change",

    # =========================
    # نام درستگی
    # =========================
    "naam": "name_correction",
    "name correction": "name_correction",
    "name change": "name_correction",
    "spell mistake": "name_correction",
    "galat naam": "name_correction",
    "correct name": "name_correction",

    # =========================
    # خاندانی معلومات اپڈیٹ
    # =========================
    "family update": "family_update",
    "khandaani": "family_update",
    "family info": "family_update",
    "family details": "family_update",
    "children add": "family_update",
    "parents update": "family_update",
}


def normalize_query(text):
    text = text.lower().strip()

    words = text.split()

    final_words = []

    for word in words:
        final_words.append(SYNONYMS.get(word, word))

    return " ".join(final_words)