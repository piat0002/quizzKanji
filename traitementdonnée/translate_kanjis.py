import json
import requests
import sys

# Configuration des fichiers et de l'API
INPUT_FILE = "kanjis-n4-og.json"
OUTPUT_FILE = "kanjis-n4-translated.json"
API_URL = "http://localhost:8080/translate"

def translate_text_list(texts, source_lang="en", target_lang="fr"):
    """
    Envoie une liste de textes à LibreTranslate en localhost (port 8080).
    """
    if not texts:
        return []

    payload = {
        "q": texts,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        # Vérification du statut HTTP
        if response.status_code == 200:
            res_data = response.json()
            # Si LibreTranslate retourne un tableau de traductions
            if isinstance(res_data, list):
                return [item.get("translatedText", "") for item in res_data]
            elif isinstance(res_data, dict):
                translated = res_data.get("translatedText", "")
                return [translated] if isinstance(texts, list) else translated
            return res_data
        else:
            print(f"   [ERREUR API] Code HTTP {response.status_code} : {response.text}")
            return texts  # Retourne le texte original si erreur API

    except requests.exceptions.RequestException as e:
        print(f"   [ERREUR CONNEXION] Impossible de contacter LibreTranslate ({e})")
        return texts  # Retourne le texte original si l'API ne répond pas

def main():
    print("=== DÉBUT DU TRAITEMENT ===")
    print(f"Chargement du fichier source : {INPUT_FILE} ...")

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            kanji_list = json.load(f)
    except FileNotFoundError:
        print(f"[ERREUR] Le fichier '{INPUT_FILE}' est introuvable dans le dossier actuel.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERREUR] Échec de la lecture du fichier JSON : {e}")
        sys.exit(1)

    total_items = len(kanji_list)
    print(f"Nombre d'éléments à traiter : {total_items}")
    print("Traduction des 'meanings' via LibreTranslate (http://localhost:8080)...\n")

    # Parcours de la liste
    for idx, item in enumerate(kanji_list, 1):
        kanji_char = item.get("kanji", "N/A")
        original_meanings = item.get("meanings", [])

        if original_meanings:
            # Appel API LibreTranslate
            translated_meanings = translate_text_list(original_meanings, source_lang="en", target_lang="fr")
            item["meanings_french"] = translated_meanings
            
            # Print de debug
            print(f"[{idx}/{total_items}] Kanji : {kanji_char}")
            print(f"   Original (EN) : {original_meanings}")
            print(f"   Traduit  (FR) : {translated_meanings}")
            print("-" * 50)
        else:
            item["meanings_french"] = []
            print(f"[{idx}/{total_items}] Kanji : {kanji_char} - (Aucun 'meanings' trouvé)")
            print("-" * 50)

    # Enregistrement du résultat dans le même dossier
    print(f"\nSauvegarde dans le fichier : {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(kanji_list, f, ensure_ascii=False, indent=2)

    print("=== TRAITEMENT TERMINÉ AVEC SUCCÈS ===")
    print(f"Le fichier traduit est disponible sous : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()