# Security Policy

## Supported Versions

Only the latest release is officially supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please **do not** report it via public GitHub Issues.

Instead, please email **arthur@example.com** (replace with real email) with "Security Vulnerability" in the subject line. We will aim to acknowledge your report within 48 hours.

## Security Best Practices for Zettel-Memory

### 1. API Key Protection

- **Never commit your `.env` file**. This project loads the `GOOGLE_API_KEY` from environment variables. Ensure `.env` is listed in your `.gitignore` (it is by default in this repo).
- Do not hardcode API keys in your Python scripts if you plan to share them.

### 2. Prompt Injection Risks

- Zettel-Memory processes memory content using LLMs. If you feed untrusted or malicious text into `brain.add_memory()`, it acts as a potential vector for **Indirect Prompt Injection**.
- While the system is designed to structure data, be cautious if you are connecting this Brain to public-facing inputs (e.g., a chatbot exposed to the internet).

### 3. Data Privacy

- **Local Storage**: By default, `brain_data` and vectors are stored locally on your machine.
- **API Privacy**: Content is sent to Google Gemini APIs for embedding and generation. Please review [Google's Generative AI Terms of Service](https://policies.google.com/terms) regarding data usage.

### 4. Dependency Management

- We try to keep dependencies (`google-genai`, `chromadb`) updated. You should regularly run `pip install --upgrade zettel-memory` (or upgrade dependencies manually) to receive security patches from upstream libraries.
