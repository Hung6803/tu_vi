# -*- coding: utf-8 -*-
"""Test Mimo API"""

import os
os.environ["MIMO_API_KEY"] = "sk-sje55hykbxti0cbgc88q78sex2kup8q0wnae1l08jicbvbu7"

from src.ai.mimo_client import MimoClient

def test_mimo():
    print("Testing Mimo API...")

    client = MimoClient()

    response = client.generate(
        user_prompt="Xin chào! Hãy giới thiệu ngắn gọn về bạn.",
        system_prompt="Bạn là một trợ lý thân thiện.",
        temperature=0.7,
    )

    # Save to file to avoid encoding issues
    with open("output/test_mimo_response.md", "w", encoding="utf-8") as f:
        f.write("# Test Mimo API Response\n\n")
        f.write(response)

    print("Response saved to output/test_mimo_response.md")
    print("--- Test completed! ---")

if __name__ == "__main__":
    test_mimo()
