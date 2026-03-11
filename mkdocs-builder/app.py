#!/usr/bin/env python3
"""
MkDocs Builder 占位符
将在任务 10 中实现
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'mkdocs-builder'}

@app.post('/build')
def build():
    return {'message': 'MkDocs builder not yet implemented', 'status': 'pending'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
