#!/usr/bin/env python3
"""
PCI DSS Compliance - Knowledge Base Ingestion Script
Simplified version for hackathon (keyword-based search)
"""

import os
import sys
import psycopg2
from psycopg2.extras import Json
import PyPDF2
from pathlib import Path
import re
from typing import List, Optional

# Environment configuration
DATABASE_URL = os.getenv('DATABASE_URL')
USE_PGVECTOR = os.getenv('USE_PGVECTOR', 'false').lower() == 'true'
CHUNK_SIZE = 1000  # words per chunk

def setup_openai():
    """Setup OpenAI client if vector mode enabled"""
    if USE_PGVECTOR:
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️  OPENAI_API_KEY not set, falling back to keyword mode")
                return None
            return OpenAI(api_key=api_key)
        except ImportError:
            print("⚠️  OpenAI package not installed, falling back to keyword mode")
            return None
    return None

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split text into chunks with word overlap"""
    words = text.split()
    chunks = []
    overlap = 100  # words overlap between chunks
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    
    return chunks

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return '\n'.join(pages)
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
        return ""

def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """Extract keywords from text for simple search"""
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    
    # Split into words and filter
    words = text.split()
    
    # Remove short words and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    keywords = []
    for word in words:
        if (len(word) > 2 and 
            word not in stop_words and 
            word.isalpha() and
            word not in keywords):
            keywords.append(word)
            
        if len(keywords) >= max_keywords:
            break
    
    return keywords

def get_connection():
    """Get PostgreSQL connection"""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        raise

def generate_embedding(text: str, client) -> Optional[str]:
    """Generate embedding using OpenAI (if available)"""
    if not client:
        return None
        
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Limit input size
        )
        vector = response.data[0].embedding
        # Format as PostgreSQL vector literal
        return '[' + ', '.join(f'{value:.6f}' for value in vector) + ']'
    except Exception as e:
        print(f"⚠️  Embedding generation failed: {e}")
        return None

def ingest_document(doc_path: str, doc_type: str, openai_client=None) -> bool:
    """Ingest a single document into knowledge base"""
    print(f"📄 Processing: {doc_path}")
    
    # Extract text
    if doc_path.endswith('.pdf'):
        text = extract_pdf_text(doc_path)
    elif doc_path.endswith(('.md', '.txt')):
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ Error reading {doc_path}: {e}")
            return False
    else:
        print(f"⚠️  Unsupported file type: {doc_path}")
        return False
    
    if not text.strip():
        print(f"⚠️  No text extracted from {doc_path}")
        return False
    
    # Split into chunks
    chunks = chunk_text(text)
    if not chunks:
        print(f"⚠️  No chunks created from {doc_path}")
        return False
    
    print(f"📝 Created {len(chunks)} chunks")
    
    # Database connection
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        for idx, chunk in enumerate(chunks):
            # Extract keywords
            keywords = extract_keywords(chunk)
            
            # Store in simple table (always)
            cur.execute("""
                INSERT INTO knowledge_simple (title, content, doc_type, keywords, source_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                f"{Path(doc_path).stem} - Chunk {idx + 1}",
                chunk,
                doc_type,
                keywords,
                'document'
            ))
            
            # Store in vector table (if enabled and available)
            if USE_PGVECTOR and openai_client:
                embedding = generate_embedding(chunk, openai_client)
                if embedding:
                    try:
                        cur.execute("""
                            INSERT INTO knowledge_embeddings 
                            (text, embedding, metadata, doc_type, source_file, chunk_index)
                            VALUES (%s, %s::vector, %s::jsonb, %s, %s, %s)
                        """, (
                            chunk,
                            embedding,
                            Json({
                                'source': Path(doc_path).name,
                                'chunk_index': idx,
                                'total_chunks': len(chunks),
                                'doc_type': doc_type
                            }),
                            doc_type,
                            Path(doc_path).name,
                            idx
                        ))
                        print(f"   ✅ Chunk {idx + 1}/{len(chunks)} (with embedding)")
                    except psycopg2.Error as e:
                        print(f"   ⚠️  Vector storage failed for chunk {idx + 1}: {e}")
                        print(f"   ✅ Chunk {idx + 1}/{len(chunks)} (keyword only)")
                else:
                    print(f"   ✅ Chunk {idx + 1}/{len(chunks)} (keyword only)")
            else:
                print(f"   ✅ Chunk {idx + 1}/{len(chunks)} (keyword only)")
        
        conn.commit()
        print(f"🎉 Successfully ingested: {doc_path}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error ingesting {doc_path}: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def main():
    """Main ingestion process"""
    print("🚀 PCI DSS Knowledge Base Ingestion")
    print("=" * 50)
    
    # Check database connection
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"📊 Database: {version}")
        
        # Check if tables exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'knowledge_simple'
        """)
        if not cur.fetchone():
            print("❌ knowledge_simple table not found. Run database schema first!")
            return False
            
        cur.close()
        conn.close()
        print("✅ Database connection OK")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    # Setup OpenAI if vector mode enabled
    openai_client = setup_openai()
    if USE_PGVECTOR:
        if openai_client:
            print("🧠 Vector mode enabled with OpenAI embeddings")
        else:
            print("⚠️  Vector mode requested but OpenAI unavailable, using keyword mode")
    else:
        print("🔤 Keyword search mode (recommended for hackathon)")
    
    # Process documents
    knowledge_base_dir = Path(__file__).parent.parent / 'knowledge_base'
    if not knowledge_base_dir.exists():
        print(f"📁 Creating knowledge_base directory: {knowledge_base_dir}")
        knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (knowledge_base_dir / 'policies').mkdir(exist_ok=True)
        (knowledge_base_dir / 'compliance').mkdir(exist_ok=True)
        
        print("📝 Please add PDF/MD files to:")
        print(f"   - {knowledge_base_dir / 'policies'} (internal policies)")
        print(f"   - {knowledge_base_dir / 'compliance'} (PCI DSS, ISO 27001 docs)")
        return True
    
    # Document folders to process
    folders = [
        (knowledge_base_dir / 'policies', 'policy'),
        (knowledge_base_dir / 'compliance', 'compliance_doc')
    ]
    
    total_processed = 0
    total_success = 0
    
    for folder_path, doc_type in folders:
        if not folder_path.exists():
            print(f"📁 Creating {folder_path}")
            folder_path.mkdir(exist_ok=True)
            continue
            
        print(f"\n📂 Processing {folder_path} ({doc_type})")
        
        # Find all PDF and MD files
        files = list(folder_path.glob('*.pdf')) + list(folder_path.glob('*.md'))
        
        if not files:
            print(f"   ⚠️  No PDF or MD files found in {folder_path}")
            continue
            
        for file_path in files:
            total_processed += 1
            if ingest_document(str(file_path), doc_type, openai_client):
                total_success += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Ingestion Summary:")
    print(f"   • Total files processed: {total_processed}")
    print(f"   • Successfully ingested: {total_success}")
    print(f"   • Failed: {total_processed - total_success}")
    
    if total_success > 0:
        # Verify ingestion
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT doc_type, COUNT(*) FROM knowledge_simple GROUP BY doc_type")
            results = cur.fetchall()
            
            print(f"\n📈 Knowledge Base Contents:")
            for doc_type, count in results:
                print(f"   • {doc_type}: {count} chunks")
                
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Could not verify ingestion: {e}")
    
    print("\n🎯 Next steps:")
    print("   1. Verify knowledge base content in database")
    print("   2. Test ChatBot knowledge search")
    print("   3. Build n8n workflows")
    
    return total_success > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)