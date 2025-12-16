#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云函数计算（SCF）统一代理处理函数
处理三类上游服务：Unifuns、Gemini、Nano Banana
"""

import json
import os
import requests
from urllib.parse import urlencode, parse_qs, urlparse


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


def main_handler(event, context):
    """
    腾讯云函数计算入口函数
    
    Args:
        event: 触发事件的数据
            - httpMethod: HTTP方法
            - path: 请求路径
            - queryString: 查询字符串
            - headers: 请求头
            - body: 请求体（字符串）
        context: 运行上下文
    
    Returns:
        dict: 包含 statusCode, headers, body 的响应
    """
    try:
        # 解析请求信息
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string = event.get('queryString', '') or ''
        headers = event.get('headers', {}) or {}
        request_body = event.get('body', '') or ''
        
        # 获取Origin头（用于CORS）
        origin = headers.get('origin', '') or headers.get('Origin', '')
        
        # 处理OPTIONS预检请求
        if method == 'OPTIONS':
            return build_cors_response(origin, {}, 200)
        
        # 健康检查
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
            return build_response(response_data, origin)
        
        # 解析查询参数
        query_params = {}
        if query_string:
            query_params = parse_qs(query_string)
            # 将列表值转换为单个值（parse_qs返回列表）
            query_params = {k: v[0] if isinstance(v, list) and len(v) > 0 else v 
                           for k, v in query_params.items()}
        
        service = query_params.get('service', '').upper()
        
        # 路由到不同的处理函数
        if service == 'UNIFUNS':
            result = handle_unifuns(query_params, request_body)
        elif service == 'GEMINI':
            result = handle_gemini(request_body)
        elif service == 'NANO_BANANA':
            result = handle_nano_banana(request_body)
        else:
            result = {'error': 'Invalid service type. Use ?service=UNIFUNS|GEMINI|NANO_BANANA'}
            return build_response(result, origin, 400)
        
        return build_response(result, origin)
        
    except Exception as e:
        error_response = {'error': str(e)}
        return build_response(error_response, origin, 500)


def build_response(data, origin, status_code=200):
    """构建HTTP响应"""
    body = json.dumps(data, ensure_ascii=False)
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }
    
    # 添加CORS头
    if origin and (origin in ALLOWED_ORIGINS or '*' in ALLOWED_ORIGINS):
        headers['Access-Control-Allow-Origin'] = origin
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        headers['Access-Control-Max-Age'] = '3600'
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }


def build_cors_response(origin, data, status_code=200):
    """构建CORS预检响应"""
    headers = {}
    
    if origin and (origin in ALLOWED_ORIGINS or '*' in ALLOWED_ORIGINS):
        headers['Access-Control-Allow-Origin'] = origin
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        headers['Access-Control-Max-Age'] = '3600'
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': ''
    }


def handle_unifuns(query_params, request_body):
    """处理Unifuns网页内容提取请求"""
    if not UNIFUNS_API_KEY:
        raise Exception('UNIFUNS_API_KEY not configured')
    
    # 从URL参数获取目标URL
    url = query_params.get('url', '')
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

