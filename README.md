# DNA-analysis-for-disease-detection-and-trait-prediction

This Flask application provides a web interface for predicting balding, obesity, and COVID-19 susceptibility based on user inputs. It integrates machine learning models and MongoDB for user authentication.

## Features

- User Authentication: Secure login using MongoDB and Flask-Bcrypt.
- Balding Prediction: Uses a pre-trained model to predict balding based on user inputs.
- Obesity Prediction: Predicts obesity category using a machine learning model.
- COVID-19 Susceptibility: Predicts susceptibility to COVID-19 based on DNA sequence similarity and user inputs.
- PDF Download: Allows users to download their prediction results as a PDF.

## Prerequisites

- Python 3
- Flask
- MongoDB
- Scikit-learn
- BioPython
- Flask-Bcrypt
- ReportLab

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up MongoDB:**

    Ensure you have MongoDB running on your local machine or update the `MONGO_URI` in the app code to point to your MongoDB instance.

5. **Run the application:**

    ```bash
    flask run
    ```

## File Structure

- **app.py:** Main application file.
- **templates/:** Directory containing HTML templates.
- **static/:** Directory containing static files (CSS, JS).
- **models/:** Directory to store the machine learning models (`.pkl` files).
- **data/:** Directory to store the required data files (e.g., `wuhan_virus.fasta`).

## Usage

1. **Navigate to the home page:**

    Open your browser and go to `http://127.0.0.1:5000/`.

2. **Login:**

    Use the login form to authenticate. If the credentials are correct, you'll be redirected to the welcome page.

3. **Make Predictions:**

    - **Balding Prediction:** Fill out the form with the required features and get the prediction result.
    - **Obesity Prediction:** Enter the necessary details to receive the obesity category prediction.
    - **COVID-19 Prediction:** Provide your DNA sequence and other details to check your susceptibility to COVID-19.

4. **Download PDF:**

    After receiving your prediction, you can download the results as a PDF.

## Notes

- Ensure the machine learning model files (`best_model.pkl`, `obesity_model.pkl`, `model_svm_on_historical.pkl`) are in the correct location.
- The `wuhan_virus.fasta` file should be present in the data directory.
- Update `app.secret_key` and other sensitive information as needed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

