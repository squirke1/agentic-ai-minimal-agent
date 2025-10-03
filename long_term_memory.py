from __future__ import annotations
import json
import uuid
import hashlib
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Simple fallback embedding function using basic text features
def simple_embedding(text: str, dim: int = 384) -> List[float]:
    """Create a simple hash-based embedding as fallback"""
    # This is a very basic fallback - in production you'd use a proper embedding model
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert hash to float array
    embedding = []
    for i in range(0, min(len(hash_bytes), dim // 8)):
        # Convert each byte to a float between -1 and 1
        embedding.extend([
            (hash_bytes[i] % 256) / 128.0 - 1.0,
            ((hash_bytes[i] >> 1) % 256) / 128.0 - 1.0,
            ((hash_bytes[i] >> 2) % 256) / 128.0 - 1.0,
            ((hash_bytes[i] >> 3) % 256) / 128.0 - 1.0
        ])
    
    # Pad to desired dimension
    while len(embedding) < dim:
        embedding.append(0.0)
    
    return embedding[:dim]

@dataclass
class Memory:
    """A memory entry with content, metadata, and embedding"""
    id: str
    content: str
    timestamp: datetime
    memory_type: str  # 'conversation', 'experience', 'fact', 'skill'
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0-1 scale

class VectorMemory:
    """Long-term memory using vector embeddings for similarity search"""
    
    def __init__(self, persist_directory: str = "./memory_db"):
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "Vector memory requires chromadb. "
                "Install with: pip install chromadb"
            )
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        except Exception:
            # Fallback for older chromadb versions
            self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="long_term_memory",
            metadata={"description": "Agent long-term memory storage"}
        )
        
        # Try to use sentence-transformers, fall back to simple embedding
        self.embedding_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Using SentenceTransformer embeddings")
        except Exception as e:
            print(f"SentenceTransformer not available ({e}), using simple embeddings")
        
        print(f"Long-term memory initialized with {self.collection.count()} existing memories")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using available method"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode([text])[0].tolist()
            except Exception as e:
                print(f"Embedding model failed ({e}), using fallback")
        
        return simple_embedding(text)
    
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for memory content"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"mem_{content_hash}_{uuid.uuid4().hex[:8]}"
    
    def store_memory(
        self, 
        content: str, 
        memory_type: str = "experience",
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> str:
        """Store a new memory with embedding"""
        if not content.strip():
            return ""
        
        memory_id = self._generate_id(content)
        timestamp = datetime.now()
        
        # Create memory object
        memory = Memory(
            id=memory_id,
            content=content,
            timestamp=timestamp,
            memory_type=memory_type,
            metadata=metadata or {},
            importance=importance
        )
        
        # Generate embedding
        embedding = self._generate_embedding(content)
        
        # Store in ChromaDB
        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    "memory_type": memory_type,
                    "timestamp": timestamp.isoformat(),
                    "importance": importance,
                    **(memory.metadata or {})
                }],
                ids=[memory_id]
            )
            print(f"Stored memory: {memory_type} - {content[:50]}...")
            return memory_id
        except Exception as e:
            print(f"Error storing memory: {e}")
            return ""
    
    def search_memories(
        self, 
        query: str, 
        n_results: int = 5,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories using semantic similarity"""
        if not query.strip():
            return []
        
        try:
            # Build query filter
            where_filter = {}
            if memory_type:
                where_filter["memory_type"] = {"$eq": memory_type}
            if min_importance > 0.0:
                where_filter["importance"] = {"$gte": min_importance}
            
            # Search with embedding
            query_embedding = self._generate_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 1.0
                    
                    memories.append({
                        "id": results['ids'][0][i],
                        "content": doc,
                        "memory_type": metadata.get('memory_type', 'unknown'),
                        "timestamp": metadata.get('timestamp', ''),
                        "importance": metadata.get('importance', 0.5),
                        "similarity": max(0.0, 1.0 - distance),  # Convert distance to similarity
                        "metadata": metadata
                    })
            
            return memories
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def get_recent_memories(
        self, 
        n_results: int = 10,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get the most recent memories"""
        try:
            where_filter = {}
            if memory_type:
                where_filter["memory_type"] = {"$eq": memory_type}
            
            results = self.collection.get(
                where=where_filter if where_filter else None,
                limit=min(n_results * 2, 100)  # Get more to sort by time
            )
            
            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    
                    memories.append({
                        "id": results['ids'][i],
                        "content": doc,
                        "memory_type": metadata.get('memory_type', 'unknown'),
                        "timestamp": metadata.get('timestamp', ''),
                        "importance": metadata.get('importance', 0.5),
                        "metadata": metadata
                    })
            
            # Sort by timestamp (most recent first)
            memories.sort(key=lambda x: x['timestamp'], reverse=True)
            return memories[:n_results]
            
        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory"""
        try:
            self.collection.delete(ids=[memory_id])
            print(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            print(f"Error deleting memory {memory_id}: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            total_count = self.collection.count()
            
            # Get all metadata to analyze
            results = self.collection.get()
            memory_types = {}
            importance_avg = 0.0
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    mem_type = metadata.get('memory_type', 'unknown')
                    memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
                    # Ensure importance is a float
                    importance = metadata.get('importance', 0.5)
                    if isinstance(importance, (int, float)):
                        importance_avg += float(importance)
                    else:
                        importance_avg += 0.5
                
                if len(results['metadatas']) > 0:
                    importance_avg /= len(results['metadatas'])
            
            return {
                "total_memories": total_count,
                "memory_types": memory_types,
                "average_importance": round(importance_avg, 2),
                "database_path": "./memory_db",
                "embedding_model": "SentenceTransformer" if self.embedding_model else "Simple"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def consolidate_memories(self, similarity_threshold: float = 0.95) -> int:
        """Remove duplicate or very similar memories"""
        try:
            results = self.collection.get()
            if not results['documents']:
                return 0
            
            documents = results['documents']
            ids = results['ids']
            
            if len(documents) < 2:
                return 0
            
            # Generate embeddings for all documents
            embeddings = [self._generate_embedding(doc) for doc in documents]
            
            # Find similar pairs
            to_delete = set()
            for i, emb1 in enumerate(embeddings):
                if ids[i] in to_delete:
                    continue
                    
                for j, emb2 in enumerate(embeddings[i+1:], i+1):
                    if ids[j] in to_delete:
                        continue
                    
                    # Calculate cosine similarity
                    try:
                        emb1_arr = np.array(emb1)
                        emb2_arr = np.array(emb2)
                        similarity = np.dot(emb1_arr, emb2_arr) / (np.linalg.norm(emb1_arr) * np.linalg.norm(emb2_arr))
                        
                        if similarity > similarity_threshold:
                            # Keep the one with higher importance
                            meta1 = results['metadatas'][i] if results['metadatas'] else {}
                            meta2 = results['metadatas'][j] if results['metadatas'] else {}
                            
                            imp1 = meta1.get('importance', 0.5)
                            imp2 = meta2.get('importance', 0.5)
                            
                            # Ensure both are floats for comparison
                            if not isinstance(imp1, (int, float)):
                                imp1 = 0.5
                            if not isinstance(imp2, (int, float)):
                                imp2 = 0.5
                            
                            if float(imp1) >= float(imp2):
                                to_delete.add(ids[j])
                            else:
                                to_delete.add(ids[i])
                    except Exception as e:
                        print(f"Error calculating similarity: {e}")
                        continue
            
            # Delete duplicates
            if to_delete:
                self.collection.delete(ids=list(to_delete))
                print(f"Consolidated {len(to_delete)} duplicate memories")
            
            return len(to_delete)
            
        except Exception as e:
            print(f"Error during memory consolidation: {e}")
            return 0