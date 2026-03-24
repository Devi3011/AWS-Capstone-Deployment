from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
import uuid
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'unified-app-2026'

# ---------------- AWS CONFIG ----------------
REGION = 'us-east-1'

try:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    sns = boto3.client('sns', region_name=REGION)

    users_table = dynamodb.Table('Users')
    registrations_table = dynamodb.Table('Registrations')

    SNS_TOPIC_ARN = 'your-sns-topic-arn'
    AWS_AVAILABLE = True
except Exception as e:
    print("AWS Error:", e)
    AWS_AVAILABLE = False

# ---------------- HELPERS ----------------
def is_logged_in():
    return 'username' in session

def send_notification(subject, message):
    if not AWS_AVAILABLE:
        print(f"[Notification] {subject}: {message}")
        return
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except Exception as e:
        print("SNS Error:", e)

# ---------------- HOME / LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if AWS_AVAILABLE:
            try:
                response = users_table.get_item(Key={'username': username})
                if 'Item' in response and response['Item']['password'] == password:
                    session['username'] = username
                    send_notification("Login", f"{username} logged in")
                    return redirect(url_for('dashboard'))
            except Exception as e:
                print(e)

        # fallback login
        if username == "admin" and password == "admin":
            session['username'] = username
            return redirect(url_for('dashboard'))

        flash("Invalid login", "danger")

    return render_template('index.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if AWS_AVAILABLE:
            try:
                users_table.put_item(Item={
                    'username': username,
                    'password': password
                })
                send_notification("New User", f"{username} registered")
            except Exception as e:
                print(e)

        flash("Account created!", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))

    data = []
    if AWS_AVAILABLE:
        try:
            response = registrations_table.scan()
            data = response.get('Items', [])
        except Exception as e:
            print(e)

    return render_template('dashboard.html',
                           username=session['username'],
                           data=data)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        entry_id = str(uuid.uuid4())

        item = {
            'id': entry_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'course': request.form['course']
        }

        if AWS_AVAILABLE:
            try:
                registrations_table.put_item(Item=item)
                send_notification("New Registration",
                                  f"{item['name']} enrolled in {item['course']}")
            except Exception as e:
                print(e)

        flash("Registered successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)