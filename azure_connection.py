from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Your OpenAI setup
openai.api_type = "azure"
openai.api_version = "2023-08-01-preview"
openai.api_base = "https://iiflopenaiservice5.openai.azure.com/"
openai.api_key = "5e7dcfd585c74970aaa42d368d5abce2"
deployment_id = "GlitchMob"

# Azure Cognitive Search setup
search_endpoint = "https://glitchmob.search.windows.net"
search_key = "Qyqh0XBcdGWoENXvU5akpSVWzSPrtPlbOw5JepvPM7AzSeD7NJc9"
search_index_name = "datasource"

def setup_byod(deployment_id: str) -> None:
    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )
    openai.requestssession = session

setup_byod(deployment_id)

@app.route('/get_completion', methods=['POST'])
def get_completion():
    try:
        data = request.get_json()
        user_message = data.get("user_message")

        completion = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": user_message}],
            deployment_id=deployment_id,
            dataSources=[
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "key": search_key,
                        "indexName": search_index_name,
                    }
                }
            ]
        )

        return jsonify(completion), 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
