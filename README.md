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
```shell
mkdir config
cd config
```
```
OPENAI_API_KEY = "your-openai-api-key"
VECTORSTORE_DIRECTORY = "vectordb"
```

## Run
1. ```shell
python -m streamlit run src\ui\home.py --server.port=8501
```
2. Visit `http://localhost:8501`