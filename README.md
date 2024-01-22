## Installation
1. Virtual environment
```shell
python -m venv .venv
.venv\Script\activate
```

2. Install packages
```shell
pip install -r requirements.txt
```

3. Create .env
```
OPENAI_API_KEY = "your-api-key-here"
VECTORSTORE_DIRECTORY = "vectordb"
```

## Run
1. run `python -m streamlit run src\ui\home.py --server.port=8501`

2. Visit `http://localhost:8501`