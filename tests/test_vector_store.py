import os
import shutil
import unittest
import numpy as np
from app.tools.vector_store import FAISSVectorStore

class TestFAISSVectorStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./tests/temp_test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        self.filepath_prefix = os.path.join(self.test_dir, "test_index")
        
        self.dimension = 8
        self.vector_store = FAISSVectorStore(dimension=self.dimension)
        
        self.docs = ["Deep learning is powerful", "Vector stores enable fast search", "FAISS is optimized in C++"]
        # Generate some random fake embeddings for the 3 docs
        self.embeddings = [
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2],
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        ]

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_and_search(self):
        self.vector_store.add_documents(self.docs, self.embeddings)
        self.assertEqual(len(self.vector_store.documents), 3)
        
        # Search using the exact same vector as doc 1
        query_emb = self.embeddings[0]
        results = self.vector_store.search(query_emb, k=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["document"], self.docs[0])
        self.assertAlmostEqual(results[0]["score"], 0.0, places=5)

    def test_save_and_load(self):
        self.vector_store.add_documents(self.docs, self.embeddings)
        self.vector_store.save(self.filepath_prefix)
        
        # Verify files were created
        self.assertTrue(os.path.exists(f"{self.filepath_prefix}.index"))
        self.assertTrue(os.path.exists(f"{self.filepath_prefix}.docs.json"))
        
        # Load in a new store
        loaded_store = FAISSVectorStore(dimension=self.dimension)
        loaded_store.load(self.filepath_prefix)
        
        self.assertEqual(len(loaded_store.documents), 3)
        self.assertEqual(loaded_store.documents, self.docs)
        
        # Search the loaded store
        query_emb = self.embeddings[1]
        results = loaded_store.search(query_emb, k=1)
        self.assertEqual(results[0]["document"], self.docs[1])

if __name__ == "__main__":
    unittest.main()
