#!/usr/bin/env zsh

cat <<'ENV' >> ~/.zshrc

# Amy agent (DeepSeek)
export DEEPSEEK_API_KEY="sk-accaaa96d975433cb844f786f219c1e0"
export AMY_LLM_MODEL="deepseek/deepseek-chat"
ENV

echo "Appended DeepSeek environment variables to ~/.zshrc"
