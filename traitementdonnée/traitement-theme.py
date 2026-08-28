import json
from pathlib import Path
from ollama import ChatResponse, chat
from pydantic import BaseModel, Field


class Categorisation(BaseModel):
    themes: list[str] = Field(
        description="Liste de 1 à 3 thèmes simples.",
        min_length=1,
        max_length=3,
    )


from ollama import Client, ChatResponse

# Définition du client Ollama avec un timeout de (120 secondes)
client = Client(timeout=120.0)

def obtenir_themes(mot_ou_concept: str) -> list[str]:
    """Interroge Ollama avec un délai de réflexion de 120 secondes."""
    try:
        response: ChatResponse = client.chat(
            model="qwen3.5:2b",
            messages=[
                {
                    "role": "system",
                    "content": (
                                        "Tu es un classificateur de vocabulaire.\n"
                "Donne 1 à 3 thèmes SIMPLES et COURTS pour le mot (mots uniques ou expressions de 2 mots max).\n\n"
                "Règles :\n"
                "- Reste sur des thèmes et domaines généraux.\n"
                "- N'utilise PAS de phrases ou de jargon complexe.\n\n"
                "Exemples :\n"
                '- "chat" -> ["animal", "compagnie"]\n'
                '- "six" -> ["nombre", "mathématiques"]\n'
                '- "ordinateur" -> ["technologie", "outil"]\n'
                '- "intervalle" -> ["temps", "espace", "musique"]\n'
                '- "courage" -> ["émotion", "vertu", "force"]\n'
                '- "montagne" -> ["nature", "paysage", "sport"]'
                    ),
                },
                {"role": "user", "content": f'Mot : "{mot_ou_concept}"'},
            ],
            format=Categorisation.model_json_schema(),
            options={
                "temperature": 0.4,
            },
        )
        
        donnees = Categorisation.model_validate_json(response.message.content)
        return [t.strip().lower() for t in donnees.themes]

    except Exception as e:
        # Affiche l'erreur exacte pour savoir ce qui s'est passé au lieu de la cacher
        print(f" [Erreur après attente : {e}]", end="")
        return ["général"]


def sauvegarder(fichier_kanjis, data, fichier_themes, themes_set):
    """Fonction utilitaire pour enregistrer l'état actuel."""
    with open(fichier_kanjis, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(fichier_themes, "w", encoding="utf-8") as f:
        json.dump(sorted(list(themes_set)), f, ensure_ascii=False, indent=2)


def traiter_kanjis(
    fichier_entree: str = "kanjis-n4-translated.json",
    fichier_sortie_kanjis: str = "kanjis-n4-with-themes.json",
    fichier_sortie_themes: str = "liste-themes-unique.json",
):
    path_entree = Path(fichier_entree)
    if not path_entree.exists():
        print(f"Erreur : Le fichier {fichier_entree} n'existe pas.")
        return

    # Si le fichier de sortie existe déjà, on reprend à partir de celui-ci !
    path_sortie = Path(fichier_sortie_kanjis)
    if path_sortie.exists():
        with open(path_sortie, "r", encoding="utf-8") as f:
            kanjis_list = json.load(f)
        print("-> Reprise à partir du fichier partiel existant.")
    else:
        with open(path_entree, "r", encoding="utf-8") as f:
            kanjis_list = json.load(f)

    ensemble_themes_uniques = set()
    # Récupérer les thèmes déjà traités si reprise
    for item in kanjis_list:
        if "themes" in item:
            ensemble_themes_uniques.update(item["themes"])

    total = len(kanjis_list)

    try:
        for index, item in enumerate(kanjis_list, 1):
            # Si le kanji a déjà été traité auparavant, on le passe
            if "themes" in item and item["themes"]:
                continue

            meanings_fr = item.get("meanings_french", [])
            meanings_en = item.get("meanings", [])

            if meanings_fr and isinstance(meanings_fr[0], list) and meanings_fr[0]:
                mot_cle = meanings_fr[0][0]
            elif meanings_fr and isinstance(meanings_fr[0], str):
                mot_cle = meanings_fr[0].split(",")[0]
            elif meanings_en:
                mot_cle = meanings_en[0]
            else:
                mot_cle = item.get("kanji", "")

            mot_cle = mot_cle.strip()
            print(f"[{index}/{total}] Kanji: {item.get('kanji')} | Mot: '{mot_cle}'", end="", flush=True)

            themes = obtenir_themes(mot_cle)
            item["themes"] = themes
            ensemble_themes_uniques.update(themes)

            print(f" -> {themes}")

            # Sauvegarde à chaque itération pour ne rien perdre si interruption
            sauvegarder(fichier_sortie_kanjis, kanjis_list, fichier_sortie_themes, ensemble_themes_uniques)

    except KeyboardInterrupt:
        print("\n\n[!] Traitement interrompu par l'utilisateur (Ctrl+C).")
        print("Les données traitées jusqu'ici ont été sauvegardées.")


if __name__ == "__main__":
    traiter_kanjis()