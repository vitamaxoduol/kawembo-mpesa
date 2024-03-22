# This module in this file is used to create helper functions
import logging
from flask import request, jsonify, Response, current_app
from datetime import datetime
import requests
import base64
# from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout
# from mpesa.stk_push import make_request_route


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://sandbox.safaricom.co.ke/oauth/v1"

def access_authentication(app, socketio):
    

    @app.route('/api/v1/get-access-token', methods=['GET'])
    def get_access_token_route() -> dict:
        try:
            if current_app.config['CONSUMER_KEY'] is None or current_app.config['CONSUMER_SECRET'] is None:
                raise ValueError("Consumer key or consumer secret is missing.")

            key_secret = f"{current_app.config['CONSUMER_KEY']}:{current_app.config['CONSUMER_SECRET']}"
            encoded_key_secret = base64.b64encode(key_secret.encode('ascii')).decode('ascii')
            url = f"{BASE_URL}/generate?grant_type=client_credentials"

            response_data = requests.get(
                url,
                headers={'Authorization': f'Basic {encoded_key_secret}'},
                timeout=30
            )

            response_data.raise_for_status()  # Raise an exception for non-200 status codes
            # return response_data.json()['access_token']  # Return only the access token
            # return jsonify({'access_token': response_data.json()['access_token']})
            return response_data.json()


        except requests.exceptions.RequestException as request_error:
            logging.error("A request error occurred: %s", request_error)
            return jsonify({"error": str(request_error)}), request_error.response.status_code

        except Exception as e:
            logging.error("An error occurred: %s", str(e))
            return jsonify({"error": str(e)}), 500
        

    @app.route('/api/v1/get-password', methods=['GET'])
    def get_password_route() -> jsonify:
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            short_code = current_app.config['SHORT_CODE']
            passkey = current_app.config['PASSKEY']
            
            if short_code is None or passkey is None:
                raise ValueError("Short code or passkey is missing.")
            
            password = f"{short_code}{passkey}{timestamp}"
            password_bytes = base64.b64encode(password.encode('utf-8'))
            password_str = password_bytes.decode('utf-8')
            return jsonify({"password": password_str}), 200
        
        except Exception as e:
            logging.error("An error occurred: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500



    # @app.route('/api/v1/make-request', methods=['GET', 'POST'])
    # def make_request_route(url: str, data: dict[str]):
    #     """
    #     This function makes a POST request with authentication to a provided URL.
    #     """
    #     try:
            
    #         # Access token retrieval
    #         access_token_response = get_access_token_route()
    #         if not access_token_response:  # Handle potential errors from get_access_token_route
    #             return None, 500

    #         access_token = access_token_response.json["access_token"]

    #         headers = {
    #             'Content-Type': 'application/json',
    #             'Authorization': f'Bearer {access_token}'
    #         }

    #         response = requests.post(url, headers=headers, json=data, timeout=30)
    #         return response.text, response.status_code

    #     except (ValueError, requests.exceptions.RequestException, Timeout) as error:
    #         logging.error("An error occurred: %s", error)
    #         return None, 500
    

    @app.route('/api/v1/lnmpesa', methods=['GET', 'POST'])
    def lnmpesa():
        try:
            base_url = "https://sandbox.safaricom.co.ke/mpesa/"
            endpoint = base_url + 'stkpush/v1/processrequest'
            # Extracting access token from the response of get_access_token_route()
            access_token_response = get_access_token_route()

            # Ensure a JSON response is returned, even for errors
            if not isinstance(access_token_response.get_data(), tuple):
                # return access_token_response
                return access_token_response[0], access_token_response[1] 

            access_token = access_token_response.json().get('access_token')
        
            logging.info("Access token: %s", access_token)
            # Constructing the Authorization header
            headers = {"Authorization": f"Bearer {access_token}"}
            # my_endpoint = base_url + "/api/v1/lnmpesa"
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password_response = get_password_route()
            password = password_response.get_json()['password']
            # password = password_response.json().get('password')
            
            

            data = {
                "BusinessShortCode": "174379",
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "PartyA": "254798820548",
                "PartyB": "600000",
                "PhoneNumber": "254798820548",
                "CallBackURL": "https://kawebo.onrender.com",
                "AccountReference": "Kawembo",
                "TransactionDesc": "Kawembo",
                "Amount": 1
            }

            res = requests.post(url=endpoint, json=data, headers=headers, timeout=100)
            logging.info(data)
            # res.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return res.json()

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., connection error, timeout)
            return jsonify({"error": str(e)}), 500

        except Exception as e:
            # Handle any other unexpected exceptions
            return jsonify({"error": "Internal server error: " + str(e)}), 500

    @app.route('/api/v1/query/', methods=['GET', 'POST'])
    def query_transaction():
        try:
            checkout_id = request.form.get('checkout_id', type=str)

            if not checkout_id:
                return jsonify({"error": "Missing checkout_id parameter"}), 400

            base_url = "https://sandbox.safaricom.co.ke"
            url = base_url + '/mpesa/stkpushquery/v1/query'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            data = {
                "BusinessShortCode": 174379,
                "Password": get_password_route(),
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_id,
            }

            response = requests.post(url=url, json=data)
            logging.info(data)

            return response.text, response.status_code

        except Exception as e:
            logging.error("An error occurred: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500
        
    

    # c2b integration
    @app.route('/api/v1/register', methods=['GET', 'POST'])
    def register_url() -> Response:
        try:
            base_url = "https://sandbox.safaricom.co.ke"
            url =base_url + '/mpesa/c2b/v1/registerurl'
            access_token = get_access_token_route()

            # # Ensure a JSON response is returned, even for errors
            # if not isinstance(access_token_response.get_data(), dict):
            #     return access_token_response

            # access_token = access_token_response.get_json()['access_token']
        
            # logging.info("Access token: %s", access_token)
            # # Constructing the Authorization header
            headers = {"Authorization": f"Bearer {access_token}"}
            data = {
                "ShortCode": 174379,
                "ResponseType": "Completed",
                "ConfirmationURL": current_app.config['CONFIRM_URL'],
                "ValidationURL": current_app.config['VALIDATE_URL'],
            }
            response =requests.post(url=url, json=data, headers=headers, timeout=100)
            return jsonify(response.json()), response.status_code

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/v1/validate/', methods=['POST'])
    def validate_url() -> Response:
        try:
            data = request.get_data().decode('utf-8')
            current_app.logger.info(data)
            return data

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/v1/confirmation/', methods=['POST'])
    def confirm_url() -> Response:
        try:
            data = request.get_data().decode('utf-8')
            current_app.logger.info(data)
            return data

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/v1/paybill', methods=['POST'])
    def paybill() -> Response:
        try:
            base_url = 'https://sandbox.safaricom.co.ke'
            url = base_url + '/mpesa/c2b/v1/simulate'
            amount = request.form.get('amount', type=float)
            tel_no = request.form.get('tel_no', type=str)
            payment_type = request.form.get('payment_type', type=str)
            bill_reference = request.form.get('bill_reference', type=str)

            # Validate input data
            if not (amount and tel_no and payment_type):
                return jsonify({"error": "Missing required parameters"}), 400

            # Additional validation/sanitization based on your requirements

            data = {
                "ShortCode": 600992,
                "CommandID": payment_type,
                "Amount": amount,
                "Msisdn": tel_no,
                "BillRefNumber": bill_reference
            }
            response =requests.post(url=url, data=data)
            return response

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    # b2c integration
    @app.route('/b2c/v1/paymentrequest', methods=['POST'])
    def process_payment_request():
        try:
            base_url = 'https://sandbox.safaricom.co.ke'
            url =   base_url + '/mpesa/b2c/v3/paymentrequest'
            amount = request.form.get('amount', type=float)
            tel_no = request.form.get('tel_no', type=str)
            payment_type = request.form.get('payment_type', type=str)
            occassion = request.form.get('occassion', type=str)

            # Validate input data
            if not (amount and tel_no and payment_type and occassion):
                return jsonify({"error": "Missing required parameters"}), 400

            if amount <= 0:
                return jsonify({"error": "Invalid amount value"}), 400

            if not tel_no.isdigit() or len(tel_no) < 10:
                return jsonify({"error": "Invalid phone number"}), 400

            if tel_no.startswith('0'):
                tel_no = '254' + tel_no[1:]

            accepted_payment_types = ['BusinessPayment', 'SalaryPayment', 'PromotionPayment']
            if payment_type not in accepted_payment_types:
                return jsonify({"error": "Invalid payment type"}), 400

            data = {
                "InitiatorName": "testapi",
                "SecurityCredential": current_app.config['SECURITY_CREDENTIALS'],
                "CommandID": payment_type,
                "Amount": amount,
                "PartyA": 600986,
                "PartyB": tel_no,
                "Remarks": "Test remarks",
                "QueueTimeOutURL": current_app.config['TIMEOUT_URL'],
                "ResultURL": current_app.config['RESULT_URL'],
                "Occasion": occassion,  # Corrected the spelling mistake in Occasion
            }

            response =make_request_route(url, data)
            return response.text, response.status_code

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/b2c/v1/result', methods=['POST'])
    def get_result():
        try:
            data = request.get_data().decode('utf-8')
            current_app.logger.info(data)
            return data

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/b2c/v1/queue', methods=['POST'])
    def get_queue():
        try:
            data = request.get_data().decode('utf-8')
            current_app.logger.info(data)
            return data

        except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({"error": "Internal server error"}), 500