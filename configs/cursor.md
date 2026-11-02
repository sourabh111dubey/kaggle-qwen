# Use the Kaggle session from Cursor

The notebook prints three values. They change every time the notebook starts. Put the key in Cursor's settings, not in this file.

1. Open Cursor Settings → Models.
2. Set the OpenAI API key to the printed `STRATA_API_KEY`. This key is for your Strata tunnel, not an OpenAI account.
3. Turn on the OpenAI base URL override and set it to the printed `STRATA_BASE_URL`. It already ends in `/v1`, for example `https://something.trycloudflare.com/v1`.
4. Add a model whose name is exactly the printed `STRATA_MODEL`. Gyro-S usually reports `gyro-s-strata`. The coder model reports `qwen3-coder-30b`. Only one of them answers at a time, whichever `MODEL` the notebook runs.

Gyro-S thinks before it answers. When Cursor keeps a reasoning block on the assistant message, send that block back on the next turn. Strata uses it to continue the same chain. Dropping it starts the reasoning over. Qwen3-Coder-30B-A3B-Instruct is an instruct model and does not need that reasoning block.

The tunnel belongs to the running notebook. When the Kaggle session stops, update the base URL and key from the new output. Do not publish the notebook output, and do not give the URL to anyone else.
