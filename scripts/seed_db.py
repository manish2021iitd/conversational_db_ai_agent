import os, json
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
import certifi

# Load .env variables
load_dotenv()
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
dbn = os.getenv("MONGODB_DB", "finance_chat")

# Use certifi for SSL CA bundle (fixes macOS Atlas TLS errors)
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client[dbn]

def load_collection(name, path):
    print(f"Loading {name} from {path} ...")
    db[name].drop()
    docs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:  # skip blank lines
                docs.append(json.loads(line))
    if docs:
        db[name].insert_many(docs)
        print(f"Inserted {len(docs)} docs into {name}")

base = os.path.dirname(os.path.dirname(__file__))
load_collection("customers", os.path.join(base, "data", "customers.json"))
load_collection("accounts", os.path.join(base, "data", "accounts.json"))
load_collection("transactions", os.path.join(base, "data", "transactions.json"))
print("Done.")
