# Coding models on a Kaggle T4×2 notebook

This repo serves one model at a time on two Tesla T4 GPUs, then lets Cursor call that session over an OpenAI-compatible API. Set `MODEL` at the top of [notebooks/strata_gyro_s.ipynb](notebooks/strata_gyro_s.ipynb).

| `MODEL` | Weights | How it runs | Download |
| --- | --- | --- | --- |
| `gyro-s` | Qwen3.8-Flash-Next Gyro-S | Strata. The n-gram table stays on disk. | About 58 GB, and about 27.6 GB of VRAM plus RAM |
| `qwen3-coder-30b` | Qwen3-Coder-30B-A3B-Instruct Q4_K_M | llama.cpp, layers split across both T4s | About 19 GB, and about 24 GB of VRAM |

Gyro-S is `Qwen3.8-Flash-Next-Gyro-S-TQ1_0.gguf` from [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF). It is the smallest published pack of those weights, so quality is below the 2-bit and 3-bit quants, and a T4 is slower than the cards in Strata’s speed tables. The coder model is `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` from [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF). Both use a 32k context so the KV cache fits.

## Why this hardware path

| | Your Kaggle session | Official FP8 checkpoint | Gyro-S on Strata |
| --- | --- | --- | --- |
| GPU | 2× Tesla T4, 16 GB each (32 GB) | About 250 GB of GPU memory | 16–24 GB cards, experts cached in VRAM |
| RAM | 29 GB | Large host RAM on top of the GPUs | Counted together with VRAM; weights need about 27.6 GB combined |
| Disk | 20 GB saved at `/kaggle/working`, plus a larger scratch disk | 173 GiB of weights | About 58.5 GB. Half of that is the n-gram table, read from disk per token |

vLLM’s FP8 recipe and the 4-bit RTX 3090 runtime do not fit a T4×2 notebook. Strata leaves the n-gram table on disk and keeps only the hot experts in VRAM.

## What you run

1. On Kaggle, enable **Internet** and the **GPU T4 x2** accelerator.
2. Upload [notebooks/strata_gyro_s.ipynb](notebooks/strata_gyro_s.ipynb) and run all cells.
3. The last cell prints `STRATA_BASE_URL` and `STRATA_API_KEY`. Copy them into `.env` (see [.env.example](.env.example)) and into Cursor ([configs/cursor.md](configs/cursor.md)). [opencode_sample.json](opencode_sample.json) lists both model ids under one provider, so it works whichever `MODEL` you ran. Point `model` at the id the notebook printed.
4. From this repo, while the notebook is still running:

```bash
pip install openai
python scripts/smoke_test.py
```

Leave the last notebook cell running. Stopping it, or hitting Kaggle’s session limit (12 hours, and the weekly GPU quota), stops the model. The Cloudflare URL changes every start.

The tunnel is for your own coding client. Kaggle’s rules forbid using notebooks as a server for other people. Do not register this URL as an OpenRouter provider: a quick-tunnel address is not a stable host, and OpenRouter private endpoints need an Enterprise account. Cursor talks to the notebook’s `/v1` API directly.

## Disk on the first run

`/kaggle/working` is only 20 GB, so the notebook will not put the weights there.

- If you attach a private Kaggle dataset that already contains the GGUF for the selected model, the notebook symlinks that file and does not copy it. Gyro-S looks for `Qwen3.8-Flash-Next-Gyro-S-TQ1_0.gguf`. The coder model looks for `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`.
- Otherwise it downloads onto the largest writable disk that has enough free space (65 GB for Gyro-S, 24 GB for the coder model). Read the model license before you upload a copy of the weights to your own Kaggle dataset for the next session.

A later session can attach that dataset and skip the download. The notebook still needs room for Strata’s small pack and draft files.

## If it does not stay up

For Gyro-S, the notebook starts with an automatic expert cache. If that start dies from lack of memory, it tries once more with a 4 GiB resident expert budget. For the coder model, a failed start retries once at a 16k context. If the second start fails, stop. Daily coding can use OpenRouter’s hosted `qwen/qwen3.8-flash` instead, which does not use this GPU.

Tesla T4 is a Turing GPU (compute capability 7.5). Strata’s ready-made engine supports that generation. If the Kaggle driver is older than 580, the notebook asks Strata for the CUDA 12 engine. llama.cpp’s published CUDA binaries need driver 570 or newer; on an older driver the notebook builds llama-server for compute capability 7.5.
