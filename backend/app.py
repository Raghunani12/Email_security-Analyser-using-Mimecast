from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time


app = Flask(__name__)


# ===========================
# CORS CONFIG
# ===========================

FRONTEND_URL = "https://email-security-analyser-using-mimec.vercel.app"


CORS(
    app,
    resources={
        r"/api/*": {
            "origins": FRONTEND_URL
        }
    },
    methods=[
        "GET",
        "POST",
        "OPTIONS"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ]
)



# ===========================
# PREFLIGHT HANDLER
# ===========================


@app.before_request
def handle_options():

    if request.method == "OPTIONS":

        response = jsonify(
            {
                "message":"CORS OK"
            }
        )


        response.headers.add(
            "Access-Control-Allow-Origin",
            FRONTEND_URL
        )


        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization"
        )


        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS"
        )


        return response






# ===========================
# TOKEN CACHE
# ===========================


token_cache = {

    "token":None,

    "expiry":0

}





# ===========================
# HEALTH CHECK
# ===========================


@app.route("/")
def home():

    return jsonify(
        {
            "status":"Mimecast API Running"
        }
    )







# ===========================
# GET TOKEN
# ===========================


@app.route(
    "/api/token",
    methods=["POST"]
)

def get_token():


    try:


        data = request.get_json()



        client_id = data.get(
            "clientId"
        )


        client_secret = data.get(
            "clientSecret"
        )


        base_url = data.get(
            "baseUrl"
        )



        if not client_id or not client_secret:

            return jsonify(
                {
                    "error":
                    "Missing credentials"
                }
            ),400




        # CACHE CHECK

        if (
            token_cache["token"]
            and
            time.time()
            <
            token_cache["expiry"]

        ):


            return jsonify(
                {

                "access_token":
                token_cache["token"]

                }
            )





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







        token_cache["token"] = result.get(
            "access_token"
        )



        token_cache["expiry"] = (

            time.time()

            +

            result.get(
                "expires_in",
                1800
            )

        )




        return jsonify(result)






    except Exception as e:


        return jsonify(
            {
                "error":str(e)
            }
        ),500








# ===========================
# SEARCH EMAIL
# ===========================


@app.route(
    "/api/search",
    methods=["POST"]
)

def search():



    try:


        data=request.get_json()



        token=data["token"]

        base_url=data["baseUrl"]





        search_payload={


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
                    "Security investigation"

                }

            ]

        }








        search_response=requests.post(


            f"{base_url}/api/message-finder/search",



            headers={


                "Authorization":
                f"Bearer {token}",



                "Content-Type":
                "application/json"

            },



            json=search_payload


        )




        search_data=search_response.json()





        print(
            "SEARCH RESPONSE"
        )

        print(search_data)





        emails=(


            search_data

            .get(
                "data",
                [{}]
            )[0]

            .get(
                "trackedEmails",
                []
            )


        )





        if not emails:


            return jsonify(
                {
                    "error":
                    "No messages found"
                }
            )







        email=emails[0]



        message_id=email.get(
            "id"
        )





        info_response=requests.post(



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





        message_info=info_response.json()






        return jsonify(


            {


            "tracking":
            email,



            "messageInfo":
            message_info


            }


        )





    except Exception as e:


        return jsonify(
            {
                "error":str(e)
            }
        ),500








# ===========================
# RUN
# ===========================


if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )
