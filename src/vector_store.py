from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class TinyVectorStore:
    def __init__(self, texts: List[str]):
        self.texts = texts
        self.v = TfidfVectorizer(ngram_range=(1,2))
        self.X = self.v.fit_transform(texts)

    def query(self, q: str, k: int = 3) -> List[Tuple[str, float]]:
        qx = self.v.transform([q])
        sims = (self.X @ qx.T).toarray().ravel()
        idx = np.argsort(-sims)[:k]
        return [(self.texts[i], float(sims[i])) for i in idx]
