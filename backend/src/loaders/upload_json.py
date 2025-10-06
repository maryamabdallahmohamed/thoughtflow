import json

class JSONPreprocessor:
    def load_and_preprocess_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)  
            except json.JSONDecodeError:
                f.seek(0)  
                return [f.read()]

        if isinstance(data, dict):
            texts = [str(v) for v in data.values() if isinstance(v, str) and len(str(v).strip()) > 0]
            return texts if texts else [str(data)]


        if isinstance(data, list):
            texts = []
            for item in data:
                if isinstance(item, dict):
                    item_texts = [str(v) for v in item.values() if isinstance(v, str) and len(str(v).strip()) > 0]
                    texts.extend(item_texts)
                elif isinstance(item, str) and len(item.strip()) > 0:
                    texts.append(item)
                else:
                    texts.append(str(item))
            return texts if texts else [str(data)]


        if isinstance(data, list):
            return [str(item) for item in data if len(str(item).strip()) > 0]


        return [str(data)]