import requests
import base64

username = "YOUR_USER_NAME"
password = "YOUR_PASSWORD"

def generate_qr_payment(amount, currency, trans_order_no):
    """ Generate QR payment request and return QR code image data """
    
    #   Prepare request payload
    data = {
        "transOrderNo": trans_order_no,
        "amt": amount,
        "currency": currency,
        "remark": "",
        "expireMinutes": 15,
        "notifyUrl": "https://NOTIFY_URL_TO_YOUR_CURRENT_BANK_REGISTER"
    }

    #   Call qr_code_request and return the result
    return qr_code_request(data)

def qr_code_request(data):
    url = "https://UAL_API_GENERATE_QR"
    
    
    
    # Encode username and password in Base64 for Basic Auth
    auth_string = f"{username}:{password}"
    base64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=data)  # Use 'json=' instead of 'data='

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")

            if "image" in content_type:
                #   Return QR Code image data
                return response.content
            else:
                #   Handle JSON response
                json_result = response.json()
                message = json_result.get("message", "⚠️ QR Code generation failed. Please try again.")
                print(message)
                return None
        else:
            print("QR Code generation failed. Please contact developer.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error making request: {e}")
        return None
