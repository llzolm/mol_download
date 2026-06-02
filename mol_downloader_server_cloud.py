#!/usr/bin/env python3
"""
MOL文件批量下载工具 - 分批处理版
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import re
import time

app = Flask(__name__)
CORS(app)

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
PUBCOM_BASE = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'

# 云端模式
IS_CLOUD = os.environ.get('PORT') is not None
TIMEOUT = 10 if IS_CLOUD else 30
MAX_RETRIES = 1 if IS_CLOUD else 3
DELAY = 0.05 if IS_CLOUD else 0.1
BATCH_SIZE = 20  # 每批处理数量

def clean_mol_file(sdf_content):
    if not sdf_content:
        return None
    lines = sdf_content.split('\n')
    clean_lines = []
    skip_mode = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('> <'):
            skip_mode = True
            continue
        if skip_mode and stripped == '':
            skip_mode = False
            continue
        if skip_mode:
            continue
        if stripped in ['$$$$', '$$']:
            break
        clean_lines.append(line)
        if stripped == 'M  END':
            break
    result = '\n'.join(clean_lines)
    if 'M  END' in result or 'M END' in result:
        return result + '\n'
    return result if clean_lines else None

def get_cid(compound_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(MAX_RETRIES):
        try:
            url = f"{PUBCOM_BASE}/compound/name/{requests.utils.quote(compound_name)}/cids/JSON"
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cids = data.get('IdentifierList', {}).get('CID', [])
                return cids[0] if cids else None
        except:
            pass
        if attempt < MAX_RETRIES - 1:
            time.sleep(2)
    return None

def download_mol(cid, compound_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(MAX_RETRIES):
        try:
            url = f"{PUBCOM_BASE}/compound/cid/{cid}/SDF"
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            if response.status_code == 200:
                mol_content = clean_mol_file(response.text)
                if mol_content and 'M' in mol_content:
                    return mol_content
        except:
            pass
        if attempt < MAX_RETRIES - 1:
            time.sleep(1)
    return None

@app.route('/')
def index():
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.route('/api/test')
def test_api():
    return jsonify({'status': 'ok', 'mode': 'cloud' if IS_CLOUD else 'local'})

@app.route('/api/search', methods=['POST'])
def search_compounds():
    data = request.get_json()
    names = data.get('names', [])
    results = []
    seen_cids = {}
    for name in names:
        cid = get_cid(name)
        if cid:
            if cid not in seen_cids:
                seen_cids[cid] = name
                results.append({'name': name, 'cid': cid, 'status': 'new'})
            else:
                results.append({'name': name, 'cid': cid, 'status': 'duplicate'})
        else:
            results.append({'name': name, 'cid': None, 'status': 'not_found'})
        time.sleep(DELAY)
    return jsonify({'results': results})

@app.route('/api/batch-download', methods=['POST'])
def batch_download():
    data = request.get_json()
    compounds = data.get('compounds', [])
    batch = data.get('batch', 0)  # 批次数
    
    start = batch * BATCH_SIZE
    end = min(start + BATCH_SIZE, len(compounds))
    batch_items = compounds[start:end]
    
    results = []
    for item in batch_items:
        name = item.get('name')
        cid = item.get('cid')
        if not cid:
            results.append({'name': name, 'success': False})
            continue
        mol_content = download_mol(cid, name)
        if mol_content:
            safe_name = re.sub(r'[\\/:*?"<>|]', '_', name)[:100]
            results.append({'name': name, 'cid': cid, 'success': True, 'mol_content': mol_content, 'filename': f"{safe_name}.mol"})
        else:
            results.append({'name': name, 'cid': cid, 'success': False})
        time.sleep(DELAY)
    
    return jsonify({
        'results': results,
        'batch': batch,
        'has_more': end < len(compounds),
        'total': len(compounds)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
