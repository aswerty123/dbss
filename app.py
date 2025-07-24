from flask import Flask,render_template,request
import joblib
from groq import Groq
import requests
import os
import sqlite3
import datetime

# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# for cloud ............

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    q = request.form.get("q")
    # db - insert
    conn = sqlite3.connect('user.db')
    conn.execute('INSERT INTO user (name, timestamp) VALUES (?,?)',(q, datetime.datetime.now()))
    conn.commit()
    conn.close()

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

@app.route("/check_spam_cv",methods=["GET","POST"])
def check_spam_cv():
    return(render_template("check_spam_cv.html"))

@app.route("/check_spam_cv_reply",methods=["GET","POST"])
def check_spam_cv_reply():
    q = request.form.get("q")

    # load model
    encoder = joblib.load('cv_encoder.pkl')
    model = joblib.load('lr_model.pkl')

    X_vec = encoder.transform([q])

    # make prediction
    pred = model.predict(X_vec)


    return(render_template("check_spam_cv_reply.html", r=pred))

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
        status = "The telegram bot is running. Please check with the telegram bot. @ntu_dsai_f1_web3_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."

    return(render_template("telegram.html", status=status))


@app.route("/stop_telegram",methods=["GET","POST"])
def stop_telegram():

    # domain_url = 'https://dsat-ft1-ipop.onrender.com'
    domain_url = request.url_root 

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    webhook_response = requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})

    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is stopped. "
    else:
        status = "Failed to stop the telegram bot. Please check the logs."
    
    return(render_template("telegram.html", status=status))

@app.route("/webhook",methods=["GET","POST"])
def webhook():

    # This endpoint will be called by Telegram when a new message is received
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        query = update["message"]["text"]

        # Pass the query to the Groq model
        client = Groq()
        completion_ds = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        response_message = completion_ds.choices[0].message.content

        # Send the response back to the Telegram chat
        send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_message_url, json={
            "chat_id": chat_id,
            "text": response_message
        })
    return('ok', 200)

@app.route("/get_user_log",methods=["GET","POST"])
def get_user_log():

    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user')
    rows = c.fetchall()
    
    c.close()
    conn.close()
    
    return(render_template("user_log.html", r=rows))

@app.route("/delete_user_log",methods=["GET","POST"])
def delete_user_log():

    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    rows_deleted = c.execute('DELETE FROM user').rowcount
 
    conn.commit()
    c.close()
    conn.close()

    r= f"Deleted {rows_deleted} rows from the user table"
    
    return(render_template("delete_log.html", r=r))

@app.route("/view_sepia",methods=["GET","POST"])
def view_sepia():
    return(render_template("view_sepia.html"))

if __name__ == "__main__":
    app.run()
