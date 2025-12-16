#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试用的后端代理服务器
用于本地开发测试，模拟阿里云函数计算的行为
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import requests
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量读取API密钥
UNIFUNS_API_KEY = os.getenv('UNIFUNS_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
NANO_BANANA_API_KEY = os.getenv('NANO_BANANA_API_KEY', '')

# API端点配置
UNIFUNS_ENDPOINT = 'https://api.302.ai/unifuncs/api/web-reader/read'
GEMINI_ENDPOINT = 'https://api.302.ai/v1/chat/completions'
NANO_BANANA_ENDPOINT = 'https://api.302.ai/google/v1/models/gemini-2.5-flash-image-preview?response_format'


@app.route('/', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Brief Proxy Server is running',
        'apis_configured': {
            'unifuns': bool(UNIFUNS_API_KEY),
            'gemini': bool(GEMINI_API_KEY),
            'nano_banana': bool(NANO_BANANA_API_KEY)
        }
    })


@app.route('/proxy', methods=['GET', 'POST'])
def proxy_handler():
    """
    统一代理处理函数
    根据请求参数转发到不同的上游服务
    """
    try:
        # 获取服务类型（前端目前只传 url，不传 service，这里做兼容）
        service = (request.args.get('service') or '').upper()

        # 如果未显式指定 service，且带有 url 参数，则默认走 UNIFUNS（网页内容提取）
        if not service and request.args.get('url'):
            service = 'UNIFUNS'

        if service == 'UNIFUNS':
            return handle_unifuns()
        elif service == 'GEMINI':
            return handle_gemini()
        elif service == 'NANO_BANANA':
            return handle_nano_banana()
        else:
            return jsonify({'error': 'Invalid service type'}), 400
            
    except Exception as e:
        print(f"代理错误: {str(e)}")
        return jsonify({'error': str(e)}), 500


def handle_unifuns():
    """处理Unifuns网页内容提取请求"""
    if not UNIFUNS_API_KEY:
        return jsonify({'error': 'UNIFUNS_API_KEY not configured'}), 500
    
    # 从URL参数获取目标URL
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400
    
    # 构建请求
    headers = {
        'Authorization': f'Bearer {UNIFUNS_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        'url': url,
        'format': 'markdown',
        'liteMode': True,
        'includeImages': False
    }
    
    try:
        response = requests.post(
            UNIFUNS_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # 返回响应
        return Response(
            response.text,
            status=response.status_code,
            mimetype='application/json'
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Unifuns request failed: {str(e)}'}), 500


def handle_gemini():
    """处理Gemini AI分析请求"""
    if not GEMINI_API_KEY:
        return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500
    
    # 获取请求体
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request body'}), 400
    except:
        return jsonify({'error': 'Invalid JSON in request body'}), 400
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # 如果使用API密钥，添加到请求头
    if GEMINI_API_KEY:
        headers['Authorization'] = f'Bearer {GEMINI_API_KEY}'
    
    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        
        return Response(
            response.text,
            status=response.status_code,
            mimetype='application/json'
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Gemini request failed: {str(e)}'}), 500


def handle_nano_banana():
    """处理Nano Banana图片生成请求"""
    if not NANO_BANANA_API_KEY:
        return jsonify({'error': 'NANO_BANANA_API_KEY not configured'}), 500
    
    # 获取请求体
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request body'}), 400
    except:
        return jsonify({'error': 'Invalid JSON in request body'}), 400
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if NANO_BANANA_API_KEY:
        headers['Authorization'] = f'Bearer {NANO_BANANA_API_KEY}'
    
    try:
        response = requests.post(
            NANO_BANANA_ENDPOINT,
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        
        return Response(
            response.text,
            status=response.status_code,
            mimetype='application/json'
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Nano Banana request failed: {str(e)}'}), 500


if __name__ == '__main__':
    # 从环境变量读取端口，默认 5000，本地测试时可用
    # 服务器部署时建议设置为 16001，例如：PORT=16001 python3 local_proxy.py
    port = int(os.getenv('PORT', '5000'))

    print("=" * 50)
    print("财经简报生成器 - 本地代理服务器")
    print("=" * 50)
    print(f"Unifuns API Key: {'已配置' if UNIFUNS_API_KEY else '未配置'}")
    print(f"Gemini API Key: {'已配置' if GEMINI_API_KEY else '未配置'}")
    print(f"Nano Banana API Key: {'已配置' if NANO_BANANA_API_KEY else '未配置'}")
    print("=" * 50)
    print(f"启动服务器: http://0.0.0.0:{port}")
    print("健康检查: GET /")
    print("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=False)

