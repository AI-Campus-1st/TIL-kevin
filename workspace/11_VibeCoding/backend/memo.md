유튜브 동영상 분석 GEMINI

pip
google-genai

https://ai.google.dev/gemini-api/docs/video-understanding?hl=ko&_gl=1*2tnv69*_up*MQ..*_ga*MTY4MTQ0MDUzMi4xNzkyMTI2NzA0*_ga_P1DBVKWT6V*czE3OTIxMjY3MDMkbzEkZzAkdDE3OTIxMjY3MDMkajYwJGwwJGg3MjEwOTI5Mjk.#youtube



RUN_LIVE_AI_TESTS=1 LIVE_YOUTUBE_URL="https://youtu.be/vM8uX9Pk-vE?si=1DAQkKTaaj_bG3-O" uv run pytest tests/services/test_recipe_analysis.py -k live -s