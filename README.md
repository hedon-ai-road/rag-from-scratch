# RAG from Scratch

This is a simple implementation of a RAG (Retrieval-Augmented Generation) system from scratch using Rust.

## Run

### Backend(Python)

```bash
cd rag-backend-py
uv sync
uv run main.py
```

### Frontend

```bash
cd rag-web
npm install
cargo tauri dev
```

## Helps

### Use camelot to extract tables from pdfs

```bash
brew install ghostscript
mkdir -p ~/lib
ln -s "$(brew --prefix gs)/lib/libgs.dylib" ~/lib
uv add camelot-py
uv add ghostscript
```
