"""
Script de teste para o endpoint OpenAI
Execute após iniciar a aplicação com: python test_openai.py
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000"
API_KEY = "sk-sua-chave-aqui"  # Substitua pela sua chave da OpenAI

def test_health_check():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    response = requests.get(f"{BASE_URL}/openai/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_simple_chat():
    """Testa uma conversa simples"""
    print("💬 Testando chat simples...")
    
    data = {
        "message": "Olá! Me diga em uma frase: o que é FastAPI?",
        "api_key": API_KEY,
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    response = requests.post(f"{BASE_URL}/openai/chat", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Resposta da IA: {result['response']}")
        print(f"Tokens usados: {result['tokens_used']}")
        print(f"Modelo: {result['model']}")
    else:
        print(f"Erro: {response.json()}")
    print()

def test_conversation_with_history():
    """Testa uma conversa com histórico"""
    print("🔄 Testando chat com histórico...")
    
    data = {
        "message": "E quais são suas principais características?",
        "api_key": API_KEY,
        "conversation_history": [
            {
                "role": "user",
                "content": "O que é FastAPI?"
            },
            {
                "role": "assistant",
                "content": "FastAPI é um framework web moderno e rápido para Python."
            }
        ],
        "max_tokens": 150
    }
    
    response = requests.post(f"{BASE_URL}/openai/chat", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Resposta da IA: {result['response']}")
        print(f"Tokens usados: {result['tokens_used']}")
    else:
        print(f"Erro: {response.json()}")
    print()

def test_invalid_api_key():
    """Testa com API key inválida"""
    print("❌ Testando API key inválida...")
    
    data = {
        "message": "Teste",
        "api_key": "chave-invalida"
    }
    
    response = requests.post(f"{BASE_URL}/openai/chat", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_empty_message():
    """Testa com mensagem vazia"""
    print("⚠️ Testando mensagem vazia...")
    
    data = {
        "message": "",
        "api_key": API_KEY
    }
    
    response = requests.post(f"{BASE_URL}/openai/chat", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TESTE DO ENDPOINT OPENAI GPT-3.5 TURBO")
    print("=" * 60)
    print()
    
    if API_KEY == "sk-sua-chave-aqui":
        print("⚠️ AVISO: Substitua API_KEY pela sua chave real da OpenAI")
        print("Os testes que requerem uma chave válida irão falhar.")
        print()
    
    try:
        # Testa health check (não precisa de API key)
        test_health_check()
        
        # Testa validações (não precisa de API key válida)
        test_invalid_api_key()
        test_empty_message()
        
        # Testes que precisam de API key válida
        if API_KEY != "sk-sua-chave-aqui":
            test_simple_chat()
            test_conversation_with_history()
        else:
            print("⏭️ Pulando testes que requerem API key válida...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("Certifique-se de que a aplicação está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    print()
    print("=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)
