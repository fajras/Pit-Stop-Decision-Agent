# Pit Stop Decision AI Agent

Ovaj projekat predstavlja softverskog AI agenta za donošenje strateških odluka o pit stopu u Formula 1 utrkama.
Agent analizira stanje utrke i na osnovu historijskih podataka i korisničkog feedbacka predlaže akciju
**PIT** ili **STAY OUT**.

## Kako pokrenuti projekat

## Prvo kreiramo virtuelno okruženje

python -m venv .venv

## Windows:

.venv\Scripts\activate

## Instalirati zavisnosti

pip install -r requirements.txt

## Pokrenuti aplikaciju

uvicorn aiagents_pitstop_web.main:app --reload

## Aplikacija će biti dostupna na:

http://127.0.0.1:8000

## Swagger će biti dostupan na:

http://127.0.0.1:8000/docs#/

## Ukoliko želimo krenuti ispočetka s novom bazom koraci su sljedeći:

## U /data obrisati pitstop.db

## Pokrenuti

uvicorn aiagents_pitstop_web.main:app --reload

## Zaustaviti aplikaciju i pokrenuti treniranje

python -m scripts.02_train_initial_model

## Seedati podatke

python -m scripts.03_seed_model_version

## Opet pokrećemo aplikaciju

uvicorn aiagents_pitstop_web.main:app --reload

## Aplikacija će biti dostupna na:

http://127.0.0.1:8000

## Swagger će biti dostupan na:

http://127.0.0.1:8000/docs#/
