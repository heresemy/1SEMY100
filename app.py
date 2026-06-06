from flask import Flask, request, jsonify, render_template_string
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
import requests
import json
import os
import like_pb2
import like_count_pb2
import uid_generator_pb2
from google.protobuf.message import DecodeError

app = Flask(__name__)

# =============================================================================
#  CONFIGURATION
# =============================================================================
ACCOUNTS_FILE = 'accounts.json'  # For GetPlayerPersonalShow tokens

# =============================================================================
#  HOMEPAGE
# =============================================================================
HOME_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SYCO FF LIKES</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }

body {
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  padding:20px;
  background: linear-gradient(45deg,#001f3f,#003366,#004080,#0059b3,#001a66,#00264d);
  color:#fff;
  font-family: Arial, sans-serif;
}

.container {
  max-width:500px;
  width:100%;
  padding:40px;
  border-radius:25px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(25px);
  box-shadow:0 20px 40px rgba(0,0,0,0.3);
  text-align:center;
}

h1 {
  font-size:2rem;
  color:#00d0ff;
  margin-bottom:10px;
}

p {
  color:#a0dfff;
  margin-bottom:30px;
  font-weight:600;
}

input {
  width:100%;
  padding:15px;
  margin-bottom:15px;
  border:none;
  border-radius:15px;
  background: rgba(255,255,255,0.15);
  color:#fff;
  font-size: 16px;
  outline:none;
}

input::placeholder {
  color: rgba(255,255,255,0.6);
}

button {
  width:100%;
  padding:15px;
  border:none;
  border-radius:15px;
  background: linear-gradient(45deg, #00d0ff, #0066ff);
  color:white;
  font-size: 18px;
  font-weight: 700;
  cursor:pointer;
  margin-bottom:20px;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.loading {
  display: none;
  margin: 15px 0;
}

.loading.show {
  display: block;
}

.spinner {
  border: 4px solid rgba(255,255,255,0.3);
  border-top: 4px solid #00d0ff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result {
  display: none;
  padding:20px;
  border-radius:15px;
  background: rgba(255,255,255,0.1);
  font-size:14px;
  text-align:left;
  white-space: pre-wrap;
  margin-top:15px;
}

.result.show {
  display: block;
}

.result.success {
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.5);
}

.result.error {
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
}

footer {
  margin-top: 20px;
  color:#8e8e93;
  font-size: 14px;
}

footer a { 
  color:#00d0ff; 
  text-decoration:none; 
}
</style>
</head>
<body>

<div class="container">
    <h1>🔥 Free Fire Likes</h1>
    <p>💎 Boost Your Likes 💎</p>

    <form id="likeForm">
        <input type="text" id="uid" placeholder="Enter Free Fire UID" required>
        <input type="text" id="server_name" placeholder="Server Name (IND, US, BR...)" required>
        <button type="submit" id="submitBtn">Send Likes 🚀</button>
    </form>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Processing...</p>
    </div>

    <div id="result" class="result"></div>

    <footer>
        Made by <a href="https://www.youtube.com/@HELPERSYCO">Creator.9XED</a>
    </footer>
</div>

<script>
const form = document.getElementById("likeForm");
const resultDiv = document.getElementById("result");
const loadingDiv = document.getElementById("loading");
const submitBtn = document.getElementById("submitBtn");

form.addEventListener("submit", async (e)=>{
    e.preventDefault();

    const uid = document.getElementById("uid").value;
    const server = document.getElementById("server_name").value;

    // Show loading
    loadingDiv.classList.add("show");
    resultDiv.classList.remove("show", "success", "error");
    resultDiv.innerHTML = "";
    submitBtn.disabled = true;

    let url = `/like?uid=${uid}&server_name=${server}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        let content;
        if (data.error) {
            resultDiv.classList.add("error");
            content = `❌ Error: ${data.error}`;
        } else {
            resultDiv.classList.add("success");
            content = `✅ SUCCESS!
━━━━━━━━━━━━━━━━
👤 Player: ${data.PlayerNickname}
🆔 UID: ${data.UID}
━━━━━━━━━━━━━━━━
❤️ Likes Before: ${data.LikesbeforeCommand}
❤️ Likes After: ${data.LikesafterCommand}
✨ Likes Given: ${data.LikesGivenByAPI}
━━━━━━━━━━━━━━━━
🔧 Successful: ${data.SuccessfulRequests}/${data.TotalRequests}`;
        }

        resultDiv.innerHTML = content;
        resultDiv.classList.add("show");
        loadingDiv.classList.remove("show");
        submitBtn.disabled = false;

    } catch(err){
        resultDiv.classList.add("error");
        resultDiv.innerHTML = "❌ Connection Error: " + err.message;
        resultDiv.classList.add("show");
        loadingDiv.classList.remove("show");
        submitBtn.disabled = false;
    }
});
</script>

</body>
</html>
'''

# =============================================================================
#  DUAL TOKEN SYSTEM
# =============================================================================

# ✅ SYSTEM 1: Load accounts from accounts.json for GetPlayerPersonalShow
def load_accounts():
    """Load UID/password pairs from accounts.json"""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading accounts.json: {e}")
    return {}

# ✅ SYSTEM 1: Fetch token from JWT API for GetPlayerPersonalShow
async def fetch_personal_token(session, uid, password):
    """Get token from JWT API using UID/password"""
    url = f"https://jwtforme.vercel.app/semy?uid={uid}&password={password}"
    try:
        async with session.get(url, timeout=10) as res:
            if res.status == 200:
                text = await res.text()
                try:
                    data = json.loads(text)
                    if isinstance(data, list) and len(data) > 0 and "token" in data[0]:
                        return data[0]["token"]
                    elif isinstance(data, dict) and "token" in data:
                        return data["token"]
                except:
                    pass
    except Exception as e:
        app.logger.error(f"Error fetching personal token: {e}")
    return None

# ✅ SYSTEM 1: Get all tokens for GetPlayerPersonalShow from accounts.json
async def get_all_personal_tokens():
    """Generate tokens from all accounts in accounts.json"""
    accounts = load_accounts()
    tokens = []
    if accounts:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_personal_token(session, uid, password) for uid, password in accounts.items()]
            results = await asyncio.gather(*tasks)
            tokens = [token for token in results if token]
    return tokens

# ✅ SYSTEM 2: Load tokens from token files for Likes
def load_like_tokens(server_name):
    """Load like tokens from token files"""
    try:
        token_files = {
            "IND": "token_ind.json",
            "BR": "token_br.json",
            "US": "token_br.json",
            "SAC": "token_br.json",
            "NA": "token_br.json"
        }
        
        file_name = token_files.get(server_name, "token_bd.json")
        
        if not os.path.exists(file_name):
            app.logger.error(f"Token file {file_name} not found")
            return []
            
        with open(file_name, "r") as f:
            tokens_data = json.load(f)
        
        # Extract token strings
        if isinstance(tokens_data, list):
            if tokens_data and isinstance(tokens_data[0], dict):
                tokens = [item.get("token") for item in tokens_data if item.get("token")]
            else:
                tokens = tokens_data
        elif isinstance(tokens_data, dict) and "tokens" in tokens_data:
            tokens = tokens_data["tokens"]
        else:
            tokens = []
            
        return tokens
    except Exception as e:
        app.logger.error(f"Error loading like tokens: {e}")
        return []

# =============================================================================
#  ENCRYPTION & PROTOBUF FUNCTIONS
# =============================================================================

def encrypt_message(plaintext):
    """Encrypt message using AES-CBC"""
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

def create_uid_protobuf(uid):
    """Create protobuf for GetPlayerPersonalShow request"""
    try:
        pb = uid_generator_pb2.uid_generator()
        pb.saturn_ = int(uid)
        pb.garena = 1
        return pb.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating UID protobuf: {e}")
        return None

def create_like_protobuf(uid):
    """Create protobuf for LikeProfile request"""
    try:
        pb = like_pb2.like()
        pb.uid = int(uid)
        return pb.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating like protobuf: {e}")
        return None

def decode_personal_show_response(binary):
    """Decode GetPlayerPersonalShow protobuf response"""
    try:
        pb = like_count_pb2.Info()
        pb.ParseFromString(binary)
        return pb
    except DecodeError as e:
        app.logger.error(f"Error decoding protobuf: {e}")
        return None

def get_server_url(server_name, endpoint_type="like"):
    """Get appropriate URL based on server and endpoint type"""
    urls = {
        "IND": {
            "like": "https://client.ind.freefiremobile.com/LikeProfile",
            "personal": "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        },
        "BR": {
            "like": "https://client.us.freefiremobile.com/LikeProfile",
            "personal": "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        },
        "US": {
            "like": "https://client.us.freefiremobile.com/LikeProfile",
            "personal": "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        },
        "SAC": {
            "like": "https://client.us.freefiremobile.com/LikeProfile",
            "personal": "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        },
        "NA": {
            "like": "https://client.us.freefiremobile.com/LikeProfile",
            "personal": "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        }
    }
    
    default_urls = {
        "like": "https://clientbp.ggblueshark.com/LikeProfile",
        "personal": "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
    }
    
    return urls.get(server_name, default_urls).get(endpoint_type, default_urls[endpoint_type])

# =============================================================================
#  REQUEST FUNCTIONS
# =============================================================================

# ✅ SYSTEM 1: GetPlayerPersonalShow using accounts.json JWT tokens
def make_personal_show_request(encrypted_uid, token, server_name):
    """Get player info using GetPlayerPersonalShow with JWT token"""
    url = get_server_url(server_name, "personal")
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
    try:
        response = requests.post(url, data=bytes.fromhex(encrypted_uid), headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            return decode_personal_show_response(response.content)
        else:
            app.logger.error(f"GetPlayerPersonalShow failed: {response.status_code}")
            return None
    except Exception as e:
        app.logger.error(f"Error in make_personal_show_request: {e}")
        return None

# ✅ SYSTEM 2: LikeProfile using token files
async def send_like_request(encrypted_uid, token, server_name):
    """Send single like using LikeProfile with like tokens"""
    url = get_server_url(server_name, "like")
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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=bytes.fromhex(encrypted_uid), headers=headers, ssl=False) as response:
                return response.status
    except Exception as e:
        app.logger.error(f"Error in send_like_request: {e}")
        return None

async def send_all_likes(uid, server_name, num_likes=220):
    """Send multiple likes using like tokens"""
    like_tokens = load_like_tokens(server_name)
    
    if not like_tokens:
        app.logger.error("No like tokens found")
        return [], 0
    
    # Use first 220 tokens
    tokens_to_use = like_tokens[:min(num_likes, len(like_tokens))]
    
    # Create and encrypt like protobuf
    like_proto = create_like_protobuf(uid)
    if not like_proto:
        return [], 0
        
    encrypted_like = encrypt_message(like_proto)
    if not encrypted_like:
        return [], 0
    
    tasks = [send_like_request(encrypted_like, token, server_name) for token in tokens_to_use]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results, len(tokens_to_use)

# =============================================================================
#  ROUTES
# =============================================================================

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

@app.route('/like', methods=['GET'])
def handle_like_request():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    
    if not uid:
        return jsonify({"error": "UID is required"}), 400
    if not server_name:
        return jsonify({"error": "Server name is required (IND, US, BR, etc.)"}), 400
    
    try:
        # ============ SYSTEM 1: Get Personal Show Tokens ============
        personal_tokens = asyncio.run(get_all_personal_tokens())
        
        if not personal_tokens:
            return jsonify({"error": "No valid accounts found in accounts.json"}), 401
        
        # Create encrypted UID for personal show
        uid_proto = create_uid_protobuf(uid)
        if not uid_proto:
            return jsonify({"error": "Failed to create UID protobuf"}), 500
            
        encrypted_uid_personal = encrypt_message(uid_proto)
        if not encrypted_uid_personal:
            return jsonify({"error": "Encryption failed"}), 500
        
        # Get player info BEFORE likes using JWT token from accounts.json
        before = make_personal_show_request(encrypted_uid_personal, personal_tokens[0], server_name)
        
        if not before:
            return jsonify({"error": "Failed to retrieve player info"}), 500
        
        before_data = json.loads(MessageToJson(before))
        likes_before = int(before_data.get('AccountInfo', {}).get('Likes', 0))
        nickname = before_data.get('AccountInfo', {}).get('PlayerNickname', 'Unknown')
        player_uid = before_data.get('AccountInfo', {}).get('UID', uid)
        
        app.logger.info(f"Likes before: {likes_before} | Player: {nickname}")
        
        # ============ SYSTEM 2: Send Likes using token files ============
        like_results, total_used = asyncio.run(send_all_likes(uid, server_name, 220))
        success_count = sum(1 for r in like_results if r == 200)
        
        app.logger.info(f"Likes sent: {success_count}/{total_used}")
        
        # Get player info AFTER likes
        after = make_personal_show_request(encrypted_uid_personal, personal_tokens[0], server_name)
        likes_after = likes_before
        
        if after:
            after_data = json.loads(MessageToJson(after))
            likes_after = int(after_data.get('AccountInfo', {}).get('Likes', likes_before))
        
        likes_given = likes_after - likes_before
        
        result = {
            "LikesGivenByAPI": likes_given,
            "LikesafterCommand": likes_after,
            "LikesbeforeCommand": likes_before,
            "PlayerNickname": nickname,
            "UID": player_uid,
            "SuccessfulRequests": success_count,
            "TotalRequests": total_used,
            "status": 1 if likes_given > 0 else 2
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
