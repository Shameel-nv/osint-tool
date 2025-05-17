from flask import Flask, render_template, request
import socket
import shodan
import phonenumbers
from phonenumbers import geocoder, carrier

app = Flask(__name__)

# 🛑 Replace with your real Shodan API key here
SHODAN_API_KEY = "bKZouw8g1PzXnC99dVkh62ASYbxtieU6"

def get_ip(domain_or_ip):
    try:
        return socket.gethostbyname(domain_or_ip)
    except:
        return None

def shodan_lookup(ip):
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        result = api.host(ip)
        return {
            'ip': ip,
            'org': result.get('org', 'N/A'),
            'os': result.get('os', 'N/A'),
            'location': result.get('location', {}),
            'ports': [item.get('port') for item in result.get('data', [])],
            'hostnames': result.get('hostnames', []),
            'domains': result.get('domains', [])
        }
    except Exception as e:
        return {'error': str(e)}

def phone_lookup(number):
    try:
        phone = phonenumbers.parse(number)
        return {
            'international_format': phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'country_name': geocoder.description_for_number(phone, "en"),
            'location': geocoder.description_for_number(phone, "en"),
            'carrier': carrier.name_for_number(phone, "en"),
            'line_type': str(phonenumbers.number_type(phone))
        }
    except:
        return {'error': 'Invalid phone number'}

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    phone = None
    if request.method == "POST":
        query = request.form.get("query").strip()
        if query.startswith("+") or query.isdigit():
            phone = phone_lookup(query)
        else:
            ip = get_ip(query)
            if ip:
                data = shodan_lookup(ip)
            else:
                data = {'error': 'Invalid domain or IP address'}
    return render_template("index.html", data=data, phone=phone)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)