# chat-with-lily
a goth chatbot

# installation
```bash
git clone https://github.com/lisphi/chat-with-lily.git
cd chat-with-lily
uv venv .venv --python=3.10
source .venv/bin/activate # for windows, run: .venv\Scripts\activate 
uv pip install --group main -e . 
```

# running
```bash
python -m lily.cli make-dataset
python -m lily.cli calc-length-cdf
```