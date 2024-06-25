from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pickle
from sklearn.svm import SVC
from Bio import SeqIO
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = 'your_secret_key'

MONGO_URI = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.6'  # Replace with your MongoDB connection URI
DB_NAME = 'flask_mongodb_demo'  # Replace with your database name
USERS_COLLECTION = 'users' 



# Establish MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[USERS_COLLECTION]

bcrypt = Bcrypt(app)



users = {
    "supreme_leader": "hesthebest"  # Example username and password
}

# Load the models and necessary data
with open('best_model.pkl', 'rb') as file:
    balding_model = pickle.load(file)

obesity_model = pickle.load(open('obesity_model.pkl', 'rb'))

with open('model_svm_on_historical.pkl', 'rb') as f:
    covid_model = pickle.load(f)

wuhan_virus_sequence = str(next(SeqIO.parse("wuhan_virus.fasta", "fasta")).seq)

obesity_label_mapping = {
    1: 'Normal_Weight', 5: 'Overweight_Level_I', 6: 'Overweight_Level_II',
    2: 'Obesity_Type_I', 0: 'Insufficient_Weight', 3: 'Obesity_Type_II',
    4: 'Obesity_Type_III'
}

@app.route('/')
def home():
    return render_template('dnaphase2.html')

@app.route('/login')
def login():
    return render_template('login.html')

# @app.route('/welcome', methods=['GET', 'POST'])
# def welcome():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         user_data = users_collection.find_one({'email': email})
#         if user_data and bcrypt.check_password_hash(user_data['password'], password):
#             session['email'] = email
#         # if username in users and users[username] == password:
#             return render_template('welcomepage.html')
#         else:
#             return render_template('login.html', error="Invalid username or password")
#     return render_template('welcomepage.html')

# @app.route("/")
# def index():
#     if 'email' in session:
#         return render_template('login.html')
#     else:
#         return redirect(url_for('login'))

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = users_collection.find_one({'email': email})
        user_name=user_data['email']
        #if user_data and bcrypt.check_password_hash(user_data['password'], password):
        if user_data and user_data['password']==password:
            session['email'] = email  # Store email in session
            session['user_name'] = user_data.get('email') # Store user name in session, with a default
            return render_template('welcomepage.html', user_name=user_name)  # Redirect to the same endpoint to handle GET
        else:
            return render_template('login.html', error='Invalid email or password.')
    
    # Retrieve the user name from the session for GET requests or after redirect
    user_name = session.get('user_name')  # Default to 'Guest' if not found
    return render_template('welcomepage.html', user_name=user_name)

# def welcome():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if email=="supreme_leader" and password=="hesthebest": # Store user name in session, with a default
#             return render_template('welcomepage.html')  # Redirect to the same endpoint to handle GET
#         else:
#             return render_template('login.html', error='Invalid email or password.')
    
#     # Retrieve the user name from the session for GET requests or after redirect
#     user_name = session.get('user_name')  # Default to 'Guest' if not found
#     return render_template('welcomepage.html')



@app.route('/index')
def next():
     return render_template('next.html')

# Balding prediction route
@app.route('/balding', methods=['GET', 'POST'])
def balding():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        features = [int(form_data.get(key)) for key in form_data if key not in ['id', 'dna_sequence']]
        prediction = balding_model.predict([features])[0]
        session['results'] = {
            'form_data': form_data,
            'prediction': f'Prediction result: {prediction}'
        }
        return redirect(url_for('results'))
    return render_template('hair_fall_.html')

# Obesity prediction route
@app.route('/obesity', methods=['GET', 'POST'])
def obesity():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        data = [int(form_data['Gender']),
                float(form_data['Age']),
                float(form_data['Height']),
                float(form_data['Weight']),
                int(form_data['family_history_with_overweight']),
                int(form_data['FAVC']),
                float(form_data['FCVC']),
                float(form_data['NCP']),
                int(form_data['CAEC']),
                int(form_data['SMOKE']),
                float(form_data['CH2O']),
                int(form_data['SCC']),
                float(form_data['FAF']),
                float(form_data['TUE']),
                int(form_data['CALC']),
                int(form_data['MTRANS'])]
        encoded_prediction = obesity_model.predict([data])[0]
        descriptive_prediction = obesity_label_mapping.get(encoded_prediction, "Unknown Category")
        session['results'] = {
            'form_data': form_data,
            'prediction': descriptive_prediction
        }
        return redirect(url_for('results'))
    return render_template('obese.html')

# COVID-19 prediction route

@app.route('/covid', methods=['GET', 'POST'])
def covid():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        dna_sequence = form_data['dna_sequence']
        age = int(form_data['age'])
        vaccination_status = int(form_data['vaccination_status'])
        similarity_score = calculate_similarity(dna_sequence, wuhan_virus_sequence)
        prediction = covid_model.predict([[age, vaccination_status, similarity_score]])[0]
        result_text = "Not susceptible to COVID-19." if prediction == 0 else "Susceptible to COVID-19."
        session['results'] = {
            'form_data': form_data,
            'prediction': result_text
        }
        return redirect(url_for('results'))
    return render_template('covid.html')


def calculate_similarity(seq1, seq2):
    max_similarity = 0
    len_wuhan = len(seq2)
    len_human = len(seq1)
    for i in range(len_wuhan - len_human + 1):
        similarity = sum(c1 == c2 for c1, c2 in zip(seq1, seq2[i:i+len_human])) / len_human
        max_similarity = max(max_similarity, similarity)
    return max_similarity

@app.route('/results')
def results():
    if 'results' not in session:
        return redirect(url_for('home'))  # Redirect to home if no results to display
    results = session['results']  # Get results from session without clearing for PDF generation
    return render_template('results.html', form_data=results['form_data'], prediction=results['prediction'])

@app.route('/download-pdf', methods=['GET', 'POST'])
def download_pdf():
    if 'results' not in session:
        return "No results available to generate PDF.", 400
    results = session['results']
    form_data = results['form_data']
    prediction = results['prediction']

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    text = p.beginText(50, 750)
    text.setFont("Helvetica", 12)
    text.textLine("Prediction Results")
    text.textLine("User Inputs:")
    for key, value in form_data.items():
        text.textLine(f"{key}: {value}")
    text.textLine("")
    text.textLine(f"Prediction: {prediction}")
    p.drawText(text)
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='prediction_results.pdf', mimetype='application/pdf')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)