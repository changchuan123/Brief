#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云函数计算统一代理处理函数
处理三类上游服务：Unifuns、Gemini、Nano Banana
"""

import json
import os
import requests
from urllib.parse import urlencode, parse_qs


# API端点配置
UNIFUNS_ENDPOINT = 'https://api.302.ai/unifuncs/api/web-reader/read'
GEMINI_ENDPOINT = 'https://api.302.ai/v1/chat/completions'
NANO_BANANA_ENDPOINT = 'https://api.302.ai/google/v1/models/gemini-2.5-flash-image-preview?response_format'

# 从环境变量读取API密钥
UNIFUNS_API_KEY = os.getenv('UNIFUNS_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
NANO_BANANA_API_KEY = os.getenv('NANO_BANANA_API_KEY', '')

# CORS白名单（从环境变量读取，支持多个域名，用逗号分隔）
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')


def handler(environ, start_response):
    """
    阿里云函数计算入口函数
    """
    try:
        # 解析请求
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')
        query_string = environ.get('QUERY_STRING', '')
        
        # 读取请求体
        request_body = ''
        if method == 'POST':
            try:
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                if content_length > 0:
                    request_body = environ['wsgi.input'].read(content_length).decode('utf-8')
            except:
                pass
        
        # 获取Origin头（用于CORS）
        origin = environ.get('HTTP_ORIGIN', '')
        
        # 处理OPTIONS预检请求
        if method == 'OPTIONS':
            return handle_cors_preflight(start_response, origin)
        
        # 根据路径和参数路由到不同的处理函数
        if path == '/' or path == '/health':
            response_data = {
                'status': 'ok',
                'message': 'Brief Proxy Server is running',
                'apis_configured': {
                    'unifuns': bool(UNIFUNS_API_KEY),
                    'gemini': bool(GEMINI_API_KEY),
                    'nano_banana': bool(NANO_BANANA_API_KEY)
                }
            }
            return send_json_response(start_response, response_data, origin)
        
        # 解析查询参数
        query_params = parse_qs(query_string)
        service = query_params.get('service', [''])[0].upper()
        
        if service == 'UNIFUNS':
            result = handle_unifuns(query_params, request_body)
        elif service == 'GEMINI':
            result = handle_gemini(request_body)
        elif service == 'NANO_BANANA':
            result = handle_nano_banana(request_body)
        else:
            result = {'error': 'Invalid service type. Use ?service=UNIFUNS|GEMINI|NANO_BANANA'}
            return send_json_response(start_response, result, origin, status=400)
        
        return send_json_response(start_response, result, origin)
        
    except Exception as e:
        error_response = {'error': str(e)}
        return send_json_response(start_response, error_response, origin, status=500)


def handle_cors_preflight(start_response, origin):
    """处理CORS预检请求"""
    headers = get_cors_headers(origin)
    headers.append(('Content-Length', '0'))
    start_response('200 OK', headers)
    return [b'']


def get_cors_headers(origin):
    """获取CORS响应头"""
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
    ]
    
    # 检查Origin是否在白名单中
    if origin and (origin in ALLOWED_ORIGINS or '*' in ALLOWED_ORIGINS):
        headers.append(('Access-Control-Allow-Origin', origin))
        headers.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'))
        headers.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization'))
        headers.append(('Access-Control-Max-Age', '3600'))
    
    return headers


def send_json_response(start_response, data, origin, status=200):
    """发送JSON响应"""
    response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    headers = get_cors_headers(origin)
    headers.append(('Content-Length', str(len(response_body))))
    
    status_text = f'{status} OK' if status == 200 else f'{status} Error'
    start_response(status_text, headers)
    return [response_body]


def handle_unifuns(query_params, request_body):
    """处理Unifuns网页内容提取请求"""
    if not UNIFUNS_API_KEY:
        raise Exception('UNIFUNS_API_KEY not configured')
    
    # 从URL参数获取目标URL
    url = query_params.get('url', [''])[0]
    if not url:
        raise Exception('Missing url parameter')
    
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
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        raise Exception(f'Unifuns request failed: {str(e)}')


def handle_gemini(request_body):
    """处理Gemini AI分析请求"""
    if not GEMINI_API_KEY:
        raise Exception('GEMINI_API_KEY not configured')
    
    # 解析请求体
    try:
        data = json.loads(request_body) if request_body else {}
        if not data:
            raise Exception('Missing request body')
    except json.JSONDecodeError:
        raise Exception('Invalid JSON in request body')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {GEMINI_API_KEY}'
    }
    
    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        raise Exception(f'Gemini request failed: {str(e)}')


def handle_nano_banana(request_body):
    """处理Nano Banana图片生成请求"""
    if not NANO_BANANA_API_KEY:
        raise Exception('NANO_BANANA_API_KEY not configured')
    
    # 解析请求体
    try:
        data = json.loads(request_body) if request_body else {}
        if not data:
            raise Exception('Missing request body')
    except json.JSONDecodeError:
        raise Exception('Invalid JSON in request body')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {NANO_BANANA_API_KEY}'
    }
    
    try:
        response = requests.post(
            NANO_BANANA_ENDPOINT,
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        raise Exception(f'Nano Banana request failed: {str(e)}')

