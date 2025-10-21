from pydantic import BaseModel, ConfigDict, Field
from mistralai import Mistral
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Union, Optional
import json
import os

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "magistral-small-latest"
# model = "ministral-8b-latest"
client = Mistral(api_key=api_key)

with open('ocr/ocr.txt', 'r') as f:
    ocr = f.read()

with open('prompt.txt', 'r') as f:
    prompt = f.read()

ocr_l = len(ocr)

class Arrondissement(BaseModel):
    nom : str = Field(..., description="Nom de l'arrondissement")
    date : str = Field(..., description="Date de rattachement de la commune à cet arrondissement")

class District(BaseModel):
    nom : str = Field(..., description="Nom du district.")
    date : str = Field(..., description="Date de rattachement de la commune à ce district.")

class Canton(BaseModel):
    nom: str = Field(..., description="Nom d'un canton de Seine-et-Marne")
    date: str = Field(..., description="Date de rattachement de la commune à ce canton")
    district: Optional[District] = Field(
        ...,
        description="Les districts sont un ancien découpage administratif. Ils sont remplacés par les arrondissements en 1800. Le champ peut être laissé vide"
    )
    arrondissement: Optional[Arrondissement] = Field(
        ...,
        description="Les arrondissements remplacent les districts. Il faut donc choisir arrondissement s'il n'y a pas de district"
    )

class Commune(BaseModel):
    nom : str = Field(..., description="Nom d'une commune de Seine-et-Marne")
    cantons : List[Canton] = Field(..., description="Liste des cantons auxquels se rattache la commune")
    texte_de_loi : Union[str, None]

class Communes(BaseModel):
    liste_des_communes : List[Commune]  = Field(..., description="Liste de toutes les communes de Seine-et-Marne")


def main():
    entries = client.chat.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{prompt}"
            },
            {
                "role": "user",
                "content": ocr
            },
        ],
        response_format=Communes,
        max_tokens=ocr_l*3,
        temperature=0
    )
    entries_dict = json.loads(entries.choices[0].message.content)
    entry_list = Communes(**entries_dict)

    with open(f"output/output_test.json", 'w', encoding='utf-8') as f:
        json.dump(entry_list.model_dump(), f, ensure_ascii=False, indent=2)
    print(entries.choices[0].message.content)
    return "Success ! \n \n \n"

main()