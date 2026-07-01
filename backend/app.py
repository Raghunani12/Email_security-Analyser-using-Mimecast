import os
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS, cross_origin
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS with explicit configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Production configuration
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("FLASK_ENV") == "development"

# ===========================
# TOKEN CACHE
# ===========================

token_cache = {
    "token": None,
    "expiry": 0
}




# ===========================
# GET TOKEN
# ===========================

@app.route("/api/token", methods=["POST", "OPTIONS"])
@cross_origin()
def get_token():

    if request.method == "OPTIONS":
        return "", 200

    data = request.json


    client_id = data.get("clientId")
    client_secret = data.get("clientSecret")
    base_url = data.get("baseUrl")



    if not client_id or not client_secret:

        return jsonify({

            "error":"Missing credentials"

        }),400




    if (
        token_cache["token"]
        and time.time() < token_cache["expiry"]
    ):


        return jsonify({

            "access_token":
            token_cache["token"]

        })




    response = requests.post(


        f"{base_url}/oauth/token",


        headers={

            "Content-Type":
            "application/x-www-form-urlencoded"

        },


        data={


            "grant_type":
            "client_credentials",


            "client_id":
            client_id,


            "client_secret":
            client_secret

        }

    )




    result = response.json()



    if response.status_code != 200:

        return jsonify(result), response.status_code




    token_cache["token"] = result["access_token"]



    token_cache["expiry"] = (

        time.time()

        +

        result.get(
            "expires_in",
            1800
        )

    )



    return jsonify(result)




# ===========================
# SEARCH + MESSAGE INFO
# ===========================

@app.route("/api/search", methods=["POST", "OPTIONS"])
@cross_origin()
def search():

    if request.method == "OPTIONS":
        return "", 200

    data = request.json



    token = data["token"]

    base_url = data["baseUrl"]




    # -----------------------
    # 1. Search email
    # -----------------------


    search_body = {


        "meta":{


            "pagination":{

                "pageSize":10

            }

        },


        "data":[


            {


            "advancedTrackAndTraceOptions":{


                "from":
                data["value"],


                "start":
                data["start"],


                "end":
                data["end"]


            },


            "searchReason":

            "Security investigation of vendor email traffic"



            }

        ]

    }




    search_response = requests.post(


        f"{base_url}/api/message-finder/search",


        headers={


            "Authorization":

            f"Bearer {token}",



            "Content-Type":

            "application/json"


        },


        json=search_body

    )



    search_data = search_response.json()



    print("SEARCH RESPONSE")
    print(search_data)




    tracked_emails = (

        search_data

        .get("data",[{}])[0]

        .get("trackedEmails",[])

    )




    if not tracked_emails:


        return jsonify({

            "error":
            "No messages found"

        })




    # -----------------------
    # Pick TOP email only
    # -----------------------


    top_email = tracked_emails[0]



    message_id = top_email.get("id")




    if not message_id:


        return jsonify({

            "error":
            "Message ID missing"

        })




    # -----------------------
    # 2. Fetch message info
    # -----------------------



    info_response = requests.post(



        f"{base_url}/api/message-finder/get-message-info",



        headers={



            "Authorization":

            f"Bearer {token}",



            "Content-Type":

            "application/json"


        },



        json={



            "data":[



                {


                    "id":
                    message_id


                }

            ]

        }


    )



    message_info = info_response.json()




    print("MESSAGE INFO RESPONSE")

    print(message_info)




    # -----------------------
    # Final response
    # -----------------------


    return jsonify({


        "tracking":

        top_email,



        "messageInfo":

        message_info



    })




# ===========================
# HEALTH CHECK
# ===========================

@app.route("/")
def home():

    return jsonify({"status": "Mimecast API Running", "version": "1.0"})

@app.route("/health")
def health():

    return jsonify({"status": "healthy"})


print(app.url_map)



if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=PORT,

        debug=DEBUG

    )
