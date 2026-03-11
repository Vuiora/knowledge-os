#!/usr/bin/env python3
"""
AI 助手占位符
将在任务 7-8 中实现
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/api/query')
def query():
    return {'message': 'AI assistant not yet implemented'}

@app.post('/api/update-embeddings')
def update_embeddings():
    return {'message': 'Embedding update not yet implemented'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
