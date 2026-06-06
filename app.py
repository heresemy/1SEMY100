from flask import Flask, request, jsonify
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
import requests
import json
import like_pb2
import like_count_pb2
import uid_generator_pb2
from google.protobuf.message import DecodeError

app = Flask(__name__)

# =============================================================================
#  BACKEND FUNCTIONS (OB53 - API JWT TOKEN SYSTEM)
# =============================================================================

def fetch_jwt_token(uid, password="M4X_BY_SEMY_km11H3EV"):
    """Fetch JWT token from API for profile visiting"""
    try:
        api_url = f"https://jwtforllike.vercel.app/kirito?uid={uid}&password={password}"
        app.logger.info(f"Fetching JWT token from API for UID: {uid}")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                jwt_token = data.get("jwt")
                region = data.get("region", "IND")
                
                app.logger.info(f"Successfully fetched JWT token for UID: {uid}, Region: {region}")
                return {
                    "jwt_token": jwt_token,
                    "region": region,
                    "success": True
                }
            else:
                app.logger.error(f"API returned success=false for UID: {uid}")
                return None
        else:
            app.logger.error(f"API request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        app.logger.error(f"Error fetching JWT token from API: {e}")
        return None

def load_tokens(server_name):
    """Load tokens from JSON files - used only for like requests"""
    try:
        if server_name == "IND":
            with open("token_ind.json", "r") as f:
                tokens = json.load(f)
        elif server_name in {"BR", "US", "SAC", "NA"}:
            with open("token_br.json", "r") as f:
                tokens = json.load(f)
        else:
            with open("token_bd.json", "r") as f:
                tokens = json.load(f)
        app.logger.info(f"Loaded {len(tokens)} tokens for server: {server_name}")
        return tokens
    except Exception as e:
        app.logger.error(f"Error loading tokens for server {server_name}: {e}")
        return None

def encrypt_message(plaintext):
    """Encrypt message using AES"""
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Error encrypting message: {e}")
        return None

def create_protobuf_message(user_id, region):
    """Create protobuf message for like request"""
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating protobuf message: {e}")
        return None

async def send_request(encrypted_uid, token, url):
    """Send single like request"""
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB53"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers) as response:
                if response.status != 200:
                    app.logger.error(f"Request failed with status code: {response.status}")
                    return response.status
                return await response.text()
    except Exception as e:
        app.logger.error(f"Exception in send_request: {e}")
        return None

async def send_multiple_requests(uid, server_name, url):
    """Send multiple like requests using tokens from file"""
    try:
        region = server_name
        protobuf_message = create_protobuf_message(uid, region)
        if protobuf_message is None:
            app.logger.error("Failed to create protobuf message.")
            return None
            
        encrypted_uid = encrypt_message(protobuf_message)
        if encrypted_uid is None:
            app.logger.error("Encryption failed.")
            return None
            
        tokens = load_tokens(server_name)
        if tokens is None:
            app.logger.error("Failed to load tokens.")
            return None
            
        tasks = []
        for i in range(220):
            token = tokens[i % len(tokens)]["token"]
            tasks.append(send_request(encrypted_uid, token, url))
            
        app.logger.info(f"Sending {len(tasks)} like requests for UID: {uid}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        app.logger.error(f"Exception in send_multiple_requests: {e}")
        return None

def create_protobuf(uid):
    """Create protobuf for profile visiting"""
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating uid protobuf: {e}")
        return None

def enc(uid):
    """Encrypt UID for profile visiting"""
    protobuf_data = create_protobuf(uid)
    if protobuf_data is None:
        return None
    encrypted_uid = encrypt_message(protobuf_data)
    return encrypted_uid

def make_request(encrypt, server_name, token):
    """Make request for profile visiting - uses JWT token from API"""
    try:
        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        else:
            url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
            
        edata = bytes.fromhex(encrypt)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB53"
        }
        
        app.logger.info(f"Visiting profile at: {url}")
        response = requests.post(url, data=edata, headers=headers, verify=False)
        hex_data = response.content.hex()
        binary = bytes.fromhex(hex_data)
        decode = decode_protobuf(binary)
        
        if decode is None:
            app.logger.error("Protobuf decoding returned None.")
        return decode
    except Exception as e:
        app.logger.error(f"Error in make_request: {e}")
        return None

def decode_protobuf(binary):
    """Decode protobuf response"""
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except DecodeError as e:
        app.logger.error(f"Error decoding Protobuf data: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Unexpected error during protobuf decoding: {e}")
        return None

# =============================================================================
#  API ROUTES
# =============================================================================

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "version": "OB53",
        "message": "Free Fire Like System - API Only"
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    
    if not uid:
        return jsonify({"error": "UID is required"}), 400
    
    if not server_name:
        return jsonify({"error": "server_name is required (IND, BR, US, etc.)"}), 400

    try:
        def process_request():
            # Step 1: Fetch JWT token from API
            app.logger.info(f"Processing like request for UID: {uid}, Server: {server_name}")
            
            jwt_data = fetch_jwt_token(uid)
            if jwt_data is None:
                raise Exception("Failed to fetch JWT token from API")
            
            jwt_token = jwt_data["jwt_token"]
            region = jwt_data["region"]
            
            app.logger.info(f"JWT token received, Region from token: {region}")

            # Step 2: Visit profile using JWT token (BEFORE)
            encrypted_uid = enc(uid)
            if encrypted_uid is None:
                raise Exception("Encryption of UID failed.")

            app.logger.info("Visiting profile BEFORE likes...")
            before = make_request(encrypted_uid, region, jwt_token)
            if before is None:
                raise Exception("Failed to retrieve initial player info.")
            
            try:
                jsone = MessageToJson(before)
            except Exception as e:
                raise Exception(f"Error converting 'before' protobuf to JSON: {e}")
            
            data_before = json.loads(jsone)
            before_like = data_before.get('AccountInfo', {}).get('Likes', 0)
            try:
                before_like = int(before_like)
            except Exception:
                before_like = 0
            
            player_name = str(data_before.get('AccountInfo', {}).get('PlayerNickname', 'Unknown'))
            player_uid = int(data_before.get('AccountInfo', {}).get('UID', uid))
            
            app.logger.info(f"Player: {player_name}, Likes BEFORE: {before_like}")

            # Step 3: Determine like URL
            if region == "IND":
                url = "https://client.ind.freefiremobile.com/LikeProfile"
            elif region in {"BR", "US", "SAC", "NA"}:
                url = "https://client.us.freefiremobile.com/LikeProfile"
            else:
                url = "https://clientbp.ggblueshark.com/LikeProfile"

            # Step 4: Send like requests using tokens from file
            app.logger.info(f"Sending likes to: {url}")
            asyncio.run(send_multiple_requests(uid, region, url))

            # Step 5: Visit profile again using JWT token (AFTER)
            app.logger.info("Visiting profile AFTER likes...")
            after = make_request(encrypted_uid, region, jwt_token)
            if after is None:
                raise Exception("Failed to retrieve player info after like requests.")
            
            try:
                jsone_after = MessageToJson(after)
            except Exception as e:
                raise Exception(f"Error converting 'after' protobuf to JSON: {e}")
            
            data_after = json.loads(jsone_after)
            after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
            
            like_given = after_like - before_like
            status = "success" if like_given > 0 else "failed"
            
            app.logger.info(f"Likes AFTER: {after_like}, Given: {like_given}")
            
            result = {
                "LikesGivenByAPI": like_given,
                "LikesbeforeCommand": before_like,
                "LikesafterCommand": after_like,
                "PlayerNickname": player_name,
                "UID": player_uid,
                "Region": region,
                "ReleaseVersion": "OB53",
                "status": status,
                "Type": "running"
            }
            return result

        result = process_request()
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)