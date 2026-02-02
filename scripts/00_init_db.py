from aiagents_pitstop_agent.infrastructure.db import engine, Base
import aiagents_pitstop_agent.infrastructure.models  # bitno da se modeli registruju

def main():
    Base.metadata.create_all(bind=engine)
    print("DB initialized")

if __name__ == "__main__":
    main()
