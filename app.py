from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_ip_info():
    # Get the IP address from the request arguments
    ip_address = request.args.get('ip')
    
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    # Construct the URL for scraping
    url = f"https://scamalytics.com/ip/{ip_address}"

    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the IP address
        ip_div = soup.find('h1')  # Find the <h1> tag
        if ip_div and 'Fraud Risk' in ip_div.text:
            ip_info = ip_div.text.split()[0]  # Extract the IP address

        # Extract the Fraud Score
        score_div = soup.find('div', class_='score')
        if score_div:
            fraud_score = score_div.text.replace('Fraud Score: ', '').strip()  # Extract the score

        # Extract the data from panel_body
        data_div = soup.find('div', class_='panel_body')
        if data_div:
            # Get the text and remove <b> tags
            data_text = data_div.get_text(separator=' ', strip=True)  # Remove <b> tags and get text

        # Create the response data
        response_data = {
            "ip address": ip_info,
            "Fraud Score": fraud_score,
            "data": data_text
        }
        
        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)