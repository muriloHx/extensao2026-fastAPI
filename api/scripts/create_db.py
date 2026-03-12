from api.database import engine
from api.models import Base

def main():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    main()
