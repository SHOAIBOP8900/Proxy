from flask import Flask, request, jsonify, make_response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    try:
        # Prepare headers from incoming request (excluding Host, etc.)
        headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'connection', 'content-length']}
        
        # Make the actual request to the target URL
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(), # For POST, PUT, PATCH
            params=request.args # Original query params are already handled by target_url
        )

        # Create a response for the client
        response = make_response(resp.content, resp.status_code)
        for k, v in resp.headers.items():
            if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                response.headers[k] = v
        
        return response

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error proxying request to {target_url}: {e}")
        return jsonify({"error": f"Proxy request failed: {str(e)}"}), 502
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # For development, you might want to enable CORS
    from flask_cors import CORS
    CORS(app) # This will allow requests from your React app's origin
    app.run(host='0.0.0.0', port=5000, debug=True)
