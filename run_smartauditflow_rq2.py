#!/usr/bin/env python3
"""CLI entrypoint for SmartAuditFlow RQ2 runner."""

import os
# 【强制离线配置】禁止 HuggingFace RAG 模型加载时连网校验
os.environ["RAG_EMBEDDING_LOCAL_ONLY"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from smartauditflow_rq2.core import main


if __name__ == "__main__":
    main()
