from flask import Flask,render_template,request
import joblib
from groq import Groq
import requests
import os

# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
# TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# for cloud ............

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    q = request.form.get("q")

    # db
    return(render_template("main.html"))

@app.route("/llama",methods=["GET","POST"])
def llama():
    return(render_template("llama.html"))

@app.route("/dpsk",methods=["GET","POST"])
def dpsk():
    return(render_template("dpsk.html"))

@app.route("/dbs",methods=["GET","POST"])
def dbs():
    return(render_template("dbs.html"))

@app.route("/prediction",methods=["GET","POST"])
def prediction():
    q = float(request.form.get("q"))

    # load model
    model = joblib.load('dbs.jl')

    # make prediction
    pred = model.predict([[q]])


    return(render_template("prediction.html", r=pred))

@app.route("/llama_reply",methods=["GET","POST"])
def llama_reply():
    q = request.form.get("q")

    # load model
    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    # print(completion.choices[0].message.content)

    return(render_template("llama_reply.html", r=completion.choices[0].message.content))

@app.route("/dpsk_reply",methods=["GET","POST"])
def dpsk_reply():
    q = request.form.get("q")

    # load model
    client = Groq()
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": q
            }
        ]
    )
    # print(completion.choices[0].message.content)

    return(render_template("dpsk_reply.html", r=completion.choices[0].message.content))

@app.route("/telegram",methods=["GET","POST"])
def telegram():
    # BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'
    domain_url = request.url_root  # Includes scheme (http/https) and domain
    # domain_url = 'https://dsat-ft1-ipop.onrender.com'

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={domain_url}/webhook"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is running. Please check with the telegram bot. @your_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."

    return(render_template("telegram.html", status=status))

if __name__ == "__main__":
    app.run()
