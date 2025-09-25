import json

class JSONPreprocessor:
    def load_and_preprocess_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)  # parse JSON
            except json.JSONDecodeError:
                # If it's not valid JSON, fallback to raw text as single item list
                f.seek(0)  # Reset file pointer
                return [f.read()]

        # If it's a dict
        if isinstance(data, dict):
            # Return list of string values from the dict
            texts = [str(v) for v in data.values() if isinstance(v, str) and len(str(v).strip()) > 0]
            return texts if texts else [str(data)]

        # If it's a list of dicts
        if isinstance(data, list):
            texts = []
            for item in data:
                if isinstance(item, dict):
                    # Extract text fields from each dict
                    item_texts = [str(v) for v in item.values() if isinstance(v, str) and len(str(v).strip()) > 0]
                    texts.extend(item_texts)
                elif isinstance(item, str) and len(item.strip()) > 0:
                    texts.append(item)
                else:
                    texts.append(str(item))
            return texts if texts else [str(data)]

        # If it's a simple list of strings
        if isinstance(data, list):
            return [str(item) for item in data if len(str(item).strip()) > 0]

        # Fallback - return as single item list
        return [str(data)]


