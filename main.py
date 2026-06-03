from flask import Flask, request, jsonify, render_template_string
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
#  PREMIUM RED & GOLD HOMEPAGE (SILENT KILLER, TRUSTED SELLER)
# =============================================================================
HOME_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SYCO FF LIKES</title>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

<style>
* { margin:0; padding:0; box-sizing:border-box; font-family: 'Inter', sans-serif; }

body {
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  padding:20px;
  overflow:hidden;
  color:#fff;
  position:relative;
}

/* Background */
body::before {
    content:"";
    position:fixed;
    width:100%;
    height:100%;
    z-index:-2;
    background: linear-gradient(45deg,#001f3f,#003366,#004080,#0059b3,#001a66,#00264d);
    background-size:600% 600%;
    animation:bgAnimate 30s ease infinite;
}
@keyframes bgAnimate {
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

/* Main Container FIXED SIZE */
.app-container { 
    position: relative;
    height: 420px;
    max-width:600px;
    width:100%;
    padding:40px;
    border-radius:25px;

    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(25px);
    box-shadow:0 20px 40px rgba(0,0,0,0.2);

    overflow:hidden;
}

/* Header */
header h1 {
  text-align:center;
  font-size:2rem;
  color:#00d0ff;
  animation:fadeInUp 1s ease forwards;
}
header p {
  text-align:center;
  color:#a0dfff;
  margin-bottom:30px;
  font-weight:600;
  animation:fadeInUp 1.3s ease forwards;
}
@keyframes fadeInUp {
  from {opacity:0; transform:translateY(20px);}
  to {opacity:1; transform:translateY(0);}
}

/* Form */
.like-form input {
    width:100%;
    padding:15px;
    margin-bottom:20px;
    border:none;
    border-radius:15px;
    background: rgba(255,255,255,0.15);
    color:#fff;
}
.like-form input::placeholder {
    color: rgba(255,255,255,0.6);
}
.like-form input:focus {
    outline:none;
    background: rgba(255,255,255,0.25);
}

/* Button */
.like-form button {
    position:relative;
    width:100%;
    padding:15px;
    border:none;
    border-radius:15px;
    background: rgba(255,255,255,0.1);
    color:white;
    cursor:pointer;
    overflow:hidden;
    backdrop-filter: blur(15px);
}

/* Light sweep */
.like-form button::before {
    content:'';
    position:absolute;
    top:0;
    left:-100%;
    width:60%;
    height:100%;
    background: rgba(255,255,255,0.25);
    transform: skewX(20deg);
    transition: left 0.8s ease;
}
.like-form button:hover::before {
    left:140%;
}

/* RESULT CARD CENTERED */
.result-card { 
    position:absolute;
    top:50%;
    left:50%;
    transform: translate(-50%, -50%) scale(0.8);

    width:85%;
    padding:20px;
    border-radius:20px;

    background: rgba(255,255,255,0.1);
    box-shadow: inset 0 5px 10px rgba(0,0,0,0.1);

    font-size:14px;
    white-space: pre-wrap;

    opacity:0;
    transition: all 1s cubic-bezier(.68,-0.55,.27,1.55);
}

/* Footer */
footer {
    position:absolute;
    bottom:20px;
    width:100%;
    text-align:center;
    color:#8e8e93;
}
footer a { color:#00d0ff; text-decoration:none; }

/* Confetti */
.confetti {
    position:fixed;
    top:0;
    left:50%;
    width:10px;
    height:10px;
    pointer-events:none;
    animation:fall 4s linear forwards;
}
@keyframes fall {
    0% { transform: translateY(0) rotate(0deg); opacity:1; }
    100% { transform: translateY(800px) rotate(360deg); opacity:0; }
}
</style>
</head>

<body>

<div class="app-container">

<header>
    <h1>🔥 Free Fire Likes</h1>
    <p>💎VIP💎 ✨Boost Your Likes!✨</p>
</header><form id="likeForm" class="like-form">
    <input type="text" id="uid" placeholder="Enter Free fire UID" required>
    <input type="text" id="server_name" placeholder="Server Name (IND, US, BR...)">
    <button type="submit">Send Likes</button>
</form><div id="result" class="result-card"></div><pre> <footer>Made by <a href="https://www.youtube.com/@HELPERSYCO">Creator.9XED                </a> 
</footer></pre>

</div>

<script>
const form = document.getElementById("likeForm");
const resultDiv = document.getElementById("result");

/* Confetti */
function createConfetti(count=60){
    for(let i=0;i<count;i++){
        const c = document.createElement('div');
        c.classList.add('confetti');
        c.style.left = Math.random()*100 + 'vw';
        c.style.background = `hsl(${Math.random()*360},80%,60%)`;
        c.style.animationDuration = 2 + Math.random()*1.5 + 's';
        document.body.appendChild(c);
        setTimeout(()=>c.remove(),3000);
    }
}

form.addEventListener("submit", async (e)=>{
    e.preventDefault();

    const uid = document.getElementById("uid").value;
    const server = document.getElementById("server_name").value;

    let url = `/like?uid=${uid}`;
    if(server) url += `&server_name=${server}`;

    /* Hide form without resizing */
    form.style.visibility = "hidden";
    form.style.position = "absolute";

    resultDiv.innerHTML = "Processing...";

    try {
        const res = await fetch(url);
        const data = await res.json();

        let content = data.error
            ? `❌ Error: ${data.error}`
            : `✅ Likes Given: ${data.LikesGivenByAPI}
Before: ${data.LikesbeforeCommand}
After: ${data.LikesafterCommand}
Player: ${data.PlayerNickname}
Region: ${data.Region}
UID: ${data.UID}`;

        resultDiv.innerHTML = content;

        setTimeout(()=>{
            resultDiv.style.opacity = "1";
            resultDiv.style.transform = "translate(-50%, -50%) scale(1)";
        },200);

        createConfetti();

    } catch(err){
        resultDiv.innerHTML = "❌ Error: " + err.message;
        createConfetti(20);
    }
});
</script>

</body>
</html>
'''

# =============================================================================
#  BACKEND FUNCTIONS (UPDATED FOR OB53)
# =============================================================================

def load_tokens(server_name):
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
        return tokens
    except Exception as e:
        app.logger.error(f"Error loading tokens for server {server_name}: {e}")
        return None

def encrypt_message(plaintext):
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
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating protobuf message: {e}")
        return None

async def send_request(encrypted_uid, token, url):
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
        tasks = []
        tokens = load_tokens(server_name)
        if tokens is None:
            app.logger.error("Failed to load tokens.")
            return None
        for i in range(220):
            token = tokens[i % len(tokens)]["token"]
            tasks.append(send_request(encrypted_uid, token, url))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        app.logger.error(f"Exception in send_multiple_requests: {e}")
        return None

def create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Error creating uid protobuf: {e}")
        return None

def enc(uid):
    protobuf_data = create_protobuf(uid)
    if protobuf_data is None:
        return None
    encrypted_uid = encrypt_message(protobuf_data)
    return encrypted_uid

def make_request(encrypt, server_name, token):
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

def fetch_player_info(uid):
    try:
        url = f"https://nr-codex-info.vercel.app/get?uid={uid}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            account_info = data.get("AccountInfo", {})
            return {
                "Level": account_info.get("AccountLevel", "NA"),
                "Region": account_info.get("AccountRegion", "NA"),
                "ReleaseVersion": account_info.get("ReleaseVersion", "NA")
            }
        else:
            app.logger.error(f"Player info API failed with status code: {response.status_code}")
            return {"Level": "NA", "Region": "NA", "ReleaseVersion": "NA"}
    except Exception as e:
        app.logger.error(f"Error fetching player info from API: {e}")
        return {"Level": "NA", "Region": "NA", "ReleaseVersion": "NA"}

# =============================================================================
#  ROUTES
# =============================================================================

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

@app.route('/api/stats')
def stats():
    return jsonify({
        "delivered": "2.5M+",
        "active": "67K+",
        "uptime": "99.99%",
        "status": "OB53 Online"
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    try:
        def process_request():
            player_info = fetch_player_info(uid)
            region = player_info["Region"]
            level = player_info["Level"]
            release_version = player_info["ReleaseVersion"]

            if region != "NA" and server_name != region:
                app.logger.warning(f"Server name {server_name} does not match API region {region}. Using API region.")
                server_name_used = region
            else:
                server_name_used = server_name

            tokens = load_tokens(server_name_used)
            if tokens is None:
                raise Exception("Failed to load tokens.")
            token = tokens[0]['token']
            encrypted_uid = enc(uid)
            if encrypted_uid is None:
                raise Exception("Encryption of UID failed.")

            before = make_request(encrypted_uid, server_name_used, token)
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
            app.logger.info(f"Likes before command: {before_like}")

            if server_name_used == "IND":
                url = "https://client.ind.freefiremobile.com/LikeProfile"
            elif server_name_used in {"BR", "US", "SAC", "NA"}:
                url = "https://client.us.freefiremobile.com/LikeProfile"
            else:
                url = "https://clientbp.ggblueshark.com/LikeProfile"

            asyncio.run(send_multiple_requests(uid, server_name_used, url))

            after = make_request(encrypted_uid, server_name_used, token)
            if after is None:
                raise Exception("Failed to retrieve player info after like requests.")
            try:
                jsone_after = MessageToJson(after)
            except Exception as e:
                raise Exception(f"Error converting 'after' protobuf to JSON: {e}")
            data_after = json.loads(jsone_after)
            after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
            player_uid = int(data_after.get('AccountInfo', {}).get('UID', 0))
            player_name = str(data_after.get('AccountInfo', {}).get('PlayerNickname', ''))
            like_given = after_like - before_like
            status = 1 if like_given != 0 else 2
            result = {
                "LikesGivenByAPI": like_given,
                "LikesafterCommand": after_like,
                "LikesbeforeCommand": before_like,
                "PlayerNickname": player_name,
                "Region": region,
                "Level": level,
                "UID": player_uid,
                "ReleaseVersion": release_version,
                "status": status,
                "OB53": "Active"
            }
            return result

        result = process_request()
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)