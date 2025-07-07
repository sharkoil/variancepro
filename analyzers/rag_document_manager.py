"""
RAG Document Manager - Handles document upload, processing, and retrieval
Provides supplementary context for enhanced LLM analysis
"""

import os
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd
import requests
import json
import re

# PDF processing imports
try:
    import PyPDF2
    import fitz  # PyMuPDF for better PDF extraction
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Text processing imports
from io import StringIO
import tempfile

class RAGDocumentManager:
    """
    Manages document upload, processing, and retrieval for RAG-enhanced analysis
    
    This class handles:
    1. PDF and text document upload and processing
    2. Document chunking and indexing for retrieval
    3. Semantic search through uploaded documents
    4. Context preparation for LLM enhancement
    """
    
    def __init__(self):
        """Initialize the RAG Document Manager"""
        self.documents: Dict[str, Dict] = {}
        self.document_chunks: Dict[str, List[Dict]] = {}
        self.session_context: List[str] = []
        self.max_chunk_size: int = 1000
        self.chunk_overlap: int = 200
        print("📚 RAG Document Manager initialized")
    
    def upload_document(self, file_path: str, document_type: str = "auto") -> Dict[str, Any]:
        """
        Upload and process a document (PDF or text)
        
        Args:
            file_path: Path to the uploaded file
            document_type: Type of document ("pdf", "txt", or "auto")
            
        Returns:
            Dictionary with upload status and document info
        """
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": "File not found"
            }
        
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())[:8]
            
            # Determine document type
            if document_type == "auto":
                document_type = self._detect_document_type(file_path)
            
            # Extract text content
            if document_type == "pdf":
                text_content = self._extract_pdf_text(file_path)
            elif document_type == "txt":
                text_content = self._extract_text_content(file_path)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported document type: {document_type}"
                }
            
            if not text_content.strip():
                return {
                    "status": "error",
                    "message": "No text content found in document"
                }
            
            # Create document metadata
            document_info = {
                "id": doc_id,
                "filename": os.path.basename(file_path),
                "type": document_type,
                "upload_time": datetime.now().isoformat(),
                "content_length": len(text_content),
                "content_hash": hashlib.md5(text_content.encode()).hexdigest()
            }
            
            # Process document into chunks
            chunks = self._chunk_document(text_content, doc_id)
            
            # Store document and chunks
            self.documents[doc_id] = document_info
            self.document_chunks[doc_id] = chunks
            
            # Add to session context for immediate use
            self._update_session_context(chunks)
            
            print(f"📄 Document uploaded: {document_info['filename']} ({len(chunks)} chunks)")
            
            return {
                "status": "success",
                "document_id": doc_id,
                "document_info": document_info,
                "chunks_created": len(chunks),
                "content_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process document: {str(e)}"
            }
    
    def _detect_document_type(self, file_path: str) -> str:
        """
        Auto-detect document type from file extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document type string
        """
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension == '.pdf':
            return 'pdf'
        elif extension in ['.txt', '.md', '.csv']:
            return 'txt'
        else:
            # Default to text for unknown extensions
            return 'txt'
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from PDF file using available PDF libraries
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not PDF_AVAILABLE:
            raise Exception("PDF processing libraries not available. Install PyPDF2 and PyMuPDF.")
        
        text_content = ""
        
        try:
            # Try PyMuPDF first (better text extraction)
            pdf_document = fitz.open(file_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text_content += page.get_text() + "\n"
            pdf_document.close()
            
        except Exception as e:
            print(f"⚠️ PyMuPDF failed, trying PyPDF2: {e}")
            
            try:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
                        
            except Exception as e2:
                raise Exception(f"Failed to extract PDF text with both libraries: {e2}")
        
        return text_content.strip()
    
    def _extract_text_content(self, file_path: str) -> str:
        """
        Extract text from text-based files
        
        Args:
            file_path: Path to text file
            
        Returns:
            Text content
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, read as binary and decode with errors='ignore'
            with open(file_path, 'rb') as file:
                return file.read().decode('utf-8', errors='ignore')
                
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")
    
    def _chunk_document(self, text: str, doc_id: str) -> List[Dict]:
        """
        Split document into overlapping chunks for better retrieval
        
        Args:
            text: Document text content
            doc_id: Document identifier
            
        Returns:
            List of document chunks with metadata
        """
        chunks = []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Split into sentences for better chunk boundaries
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_size = len(sentence)
            
            # If adding this sentence exceeds max chunk size, create a new chunk
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                # Create chunk with overlap from previous chunk
                chunks.append({
                    "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                    "document_id": doc_id,
                    "chunk_index": chunk_index,
                    "content": current_chunk.strip(),
                    "content_length": len(current_chunk),
                    "created_at": datetime.now().isoformat()
                })
                
                # Start new chunk with overlap
                overlap_words = current_chunk.split()[-self.chunk_overlap//10:]  # Approximate word overlap
                current_chunk = " ".join(overlap_words) + " " + sentence
                current_size = len(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                current_chunk += " " + sentence if current_chunk else sentence
                current_size += sentence_size
        
        # Add final chunk if there's remaining content
        if current_chunk.strip():
            chunks.append({
                "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                "document_id": doc_id,
                "chunk_index": chunk_index,
                "content": current_chunk.strip(),
                "content_length": len(current_chunk),
                "created_at": datetime.now().isoformat()
            })
        
        return chunks
    
    def _update_session_context(self, chunks: List[Dict]) -> None:
        """
        Update session context with new document chunks
        
        Args:
            chunks: List of document chunks to add to context
        """
        # Add chunk content to session context
        for chunk in chunks:
            self.session_context.append(chunk["content"])
        
        # Limit session context size to prevent overwhelming the LLM
        max_context_chunks = 20
        if len(self.session_context) > max_context_chunks:
            self.session_context = self.session_context[-max_context_chunks:]
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search through uploaded documents for relevant content
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant document chunks
        """
        if not self.document_chunks:
            return []
        
        query_lower = query.lower()
        scored_chunks = []
        
        # Simple keyword-based scoring for now
        # In production, this could be enhanced with embedding-based similarity
        for doc_id, chunks in self.document_chunks.items():
            for chunk in chunks:
                content_lower = chunk["content"].lower()
                
                # Calculate relevance score based on keyword matches
                score = 0
                query_words = query_lower.split()
                
                for word in query_words:
                    if word in content_lower:
                        # More weight for exact matches
                        score += content_lower.count(word) * 2
                        
                        # Additional weight for proximity to other query words
                        for other_word in query_words:
                            if other_word != word and other_word in content_lower:
                                score += 1
                
                if score > 0:
                    chunk_result = chunk.copy()
                    chunk_result["relevance_score"] = score
                    chunk_result["document_filename"] = self.documents[doc_id]["filename"]
                    scored_chunks.append(chunk_result)
        
        # Sort by relevance score and return top results
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:max_results]
    
    def get_enhanced_context_for_llm(self, analysis_type: str, data_context: str) -> str:
        """
        Generate enhanced context for LLM analysis using uploaded documents
        
        Args:
            analysis_type: Type of analysis being performed (variance, trends, top_n)
            data_context: Context about the data being analyzed
            
        Returns:
            Enhanced context string for LLM
        """
        if not self.session_context:
            return ""
        
        # Create analysis-specific search query
        search_queries = {
            "variance": f"variance analysis budget actual performance {data_context}",
            "trends": f"trends patterns forecast growth decline {data_context}",
            "top_n": f"ranking performance top bottom comparison {data_context}",
            "general": f"analysis insights recommendations {data_context}"
        }
        
        search_query = search_queries.get(analysis_type, search_queries["general"])
        
        # Search for relevant document content
        relevant_chunks = self.search_documents(search_query, max_results=3)
        
        if not relevant_chunks:
            # Use recent session context if no specific matches
            context_content = "\n".join(self.session_context[:3])
        else:
            # Use most relevant chunks
            context_content = "\n".join([chunk["content"] for chunk in relevant_chunks])
        
        # Format enhanced context
        enhanced_context = f"""
SUPPLEMENTARY ANALYSIS CONTEXT:
Based on uploaded documents and domain knowledge:

{context_content}

Please incorporate insights from this supplementary context into your analysis, 
particularly focusing on industry standards, best practices, and relevant benchmarks 
that may inform the interpretation of the data patterns.
"""
        
        return enhanced_context
    
    def get_document_summary(self) -> Dict[str, Any]:
        """
        Get summary of all uploaded documents
        
        Returns:
            Summary dictionary with document statistics
        """
        if not self.documents:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "context_size": 0
            }
        
        total_chunks = sum(len(chunks) for chunks in self.document_chunks.values())
        
        document_list = []
        for doc_id, doc_info in self.documents.items():
            chunk_count = len(self.document_chunks.get(doc_id, []))
            document_list.append({
                "id": doc_id,
                "filename": doc_info["filename"],
                "type": doc_info["type"],
                "upload_time": doc_info["upload_time"],
                "chunks": chunk_count,
                "content_length": doc_info["content_length"]
            })
        
        return {
            "total_documents": len(self.documents),
            "total_chunks": total_chunks,
            "context_size": len(self.session_context),
            "documents": document_list
        }
    
    def remove_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Remove a document and its chunks from the system
        
        Args:
            doc_id: Document ID to remove
            
        Returns:
            Operation result
        """
        if doc_id not in self.documents:
            return {
                "status": "error",
                "message": "Document not found"
            }
        
        try:
            # Remove document chunks from session context
            if doc_id in self.document_chunks:
                chunks_to_remove = [chunk["content"] for chunk in self.document_chunks[doc_id]]
                for chunk_content in chunks_to_remove:
                    if chunk_content in self.session_context:
                        self.session_context.remove(chunk_content)
                
                del self.document_chunks[doc_id]
            
            # Remove document metadata
            filename = self.documents[doc_id]["filename"]
            del self.documents[doc_id]
            
            return {
                "status": "success",
                "message": f"Document '{filename}' removed successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to remove document: {str(e)}"
            }
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """
        Clear all documents and reset the system
        
        Returns:
            Operation result
        """
        try:
            doc_count = len(self.documents)
            
            self.documents.clear()
            self.document_chunks.clear()
            self.session_context.clear()
            
            return {
                "status": "success",
                "message": f"Cleared {doc_count} documents and reset context"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to clear documents: {str(e)}"
            }
    
    def has_documents(self) -> bool:
        """
        Check if any documents are currently uploaded
        
        Returns:
            bool: True if documents are available, False otherwise
        """
        return len(self.documents) > 0
