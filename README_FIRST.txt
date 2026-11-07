MYTUBE AI — CONSOLIDATED ENGINE v0.5

Targeted fix for the 35% generation stall: the previous backend wrote progress to SQLite for every Ollama stream chunk. This release throttles progress writes to reduce database lock and I/O pressure during long generations.

Apply by extracting this ZIP into the existing repository root and replacing files. Then restart the backend with: bash start.sh

Text generation uses local Ollama qwen2.5:3b. Image, video, voice and music engines are still not connected. No paid API or billing is enabled.
