import os, json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGODB_URI","mongodb://localhost:27017")
dbn = os.getenv("MONGODB_DB","finance_chat")

client = MongoClient(uri)
db = client[dbn]

def load_collection(name, path):
    print(f"Loading {name} from {path} ...")
    db[name].drop()
    docs = [json.loads(line) for line in open(path, "r")]
    if docs:
        db[name].insert_many(docs)
        print(f"Inserted {len(docs)} docs into {name}")

base = os.path.dirname(os.path.dirname(__file__))
load_collection("customers", os.path.join(base, "data", "customers.json"))
load_collection("accounts", os.path.join(base, "data", "accounts.json"))
load_collection("transactions", os.path.join(base, "data", "transactions.json"))
print("Done.")
