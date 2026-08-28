from typing import Annotated
from ollama import ChatResponse, chat
from pydantic import BaseModel, Field


# Syntaxe moderne Pydantic V2 : min_length / max_length
class Categorisation(BaseModel):
    themes: list[str] = Field(
        description="Liste de 1 à 3 thèmes simples (un ou deux mots max par thème).",
        min_length=1,
        max_length=3,
    )


mot_a_tester = "volcan"

response: ChatResponse = chat(
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
        {"role": "user", "content": f'Mot à classifier : "{mot_a_tester}"'},
    ],
    format=Categorisation.model_json_schema(),
    options={"temperature": 0.3},
)

print(response.message.content)
#print(response['message']['content'])
# or access fields directly from the response object
#print(response.message.content)