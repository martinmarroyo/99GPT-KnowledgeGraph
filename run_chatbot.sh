#!/bin/bash

set -e

streamlit run src/app.py -- \
    --config src/configs/azure/model_config.yaml src/configs/chatbot_config.yaml \
    --from_env
