#!/bin/bash

# ASD Support App - Quick Start Script

echo "🌟 ASD支援アプリを起動します..."

# 環境変数ファイルの確認
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    echo "📝 .env.exampleをコピーして.envファイルを作成してください"
    echo ""
    echo "コマンド: cp .env.example .env"
    echo "その後、.envファイルを編集してOpenAI APIキーを設定してください"
    exit 1
fi

# 仮想環境の確認
if [ ! -d "venv" ] && [ ! -d "env_a" ]; then
    echo "📦 仮想環境が見つかりません"
    echo "作成しますか？ (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        echo "仮想環境を手動で作成してください"
        exit 1
    fi
else
    # 仮想環境の有効化
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "env_a" ]; then
        source env_a/bin/activate
    fi
fi

# Streamlitアプリの起動
echo "🚀 アプリを起動します..."
streamlit run app/main.py

