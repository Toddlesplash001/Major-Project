from flask import Blueprint, render_template, request
from services.crop_service import recommend_crop
from services.pest_service import predict_disease
from flask import flash, redirect, url_for
import requests
web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def home():
    return render_template("home.html")

@web_bp.route("/services")
def services():
    return render_template("home.html")


@web_bp.route("/crop_form")
def crop_form():
    return render_template("crop_form.html")

@web_bp.route("/crop", methods=["POST"])
def crop_predict():
    N = float(request.form.get("N"))
    P = float(request.form.get("P"))
    K = float(request.form.get("K"))
    temperature = float(request.form.get("temperature"))
    humidity = float(request.form.get("humidity"))
    ph = float(request.form.get("ph"))
    rainfall = float(request.form.get("rainfall"))

    result = recommend_crop(N, P, K, temperature, humidity, ph, rainfall)

    return render_template("crop_result.html", 
                         crop_name=result,
                         N=N, P=P, K=K, 
                         temperature=temperature, 
                         humidity=humidity, 
                         ph=ph, 
                         rainfall=rainfall)


from services.fertilizer_service import recommend_fertilizer

@web_bp.route("/fertilizer_form")
def fertilizer_form():
    return render_template("fertilizer_form.html")

@web_bp.route("/fertilizer", methods=["POST"])
def fertilizer_predict():
    N = float(request.form.get("N"))
    P = float(request.form.get("P"))
    K = float(request.form.get("K"))

    result = recommend_fertilizer(N, P, K)

    return render_template("fertilizer_result.html", 
                         fertilizer_name=result,
                         N=N, P=P, K=K)


from services.weather_service import get_weather, crop_alert, general_weather_alerts

# Weather form page
@web_bp.route("/weather_form")
def weather_form():
    return render_template("weather_form.html")

# Handle form submission
def get_city_from_ip(ip):
    """Very simple IP → City lookup"""
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()

        if data.get("status") != "success":
            return None

        return data.get("city")   # return only city
    except:
        return None


@web_bp.route("/weather", methods=["POST"])
def weather_result():
    # # 1️⃣ Get user's IP
    # user_ip = requests.get("https://api.ipify.org").text
    # print("Public IP:", user_ip)
    # # user_ip = request.remote_addr
    # print("User IP:", user_ip)
    # # 2️⃣ Convert IP → City
    # city = get_city_from_ip(user_ip)
    city = "Chandigarh"
    if not city:
        city = "Unknown"

    # 3️⃣ Get weather using your existing function
    weather_data = get_weather(city)
    
    # 4️⃣ Generate alerts
    alerts = crop_alert(weather_data)
    general_alerts = general_weather_alerts(weather_data)

    # 5️⃣ Render results
    return render_template(
        "weather_result.html",
        city=city,
        weather=weather_data,
        alerts=alerts,
        general_alerts=general_alerts
    )

@web_bp.route("/flowise")
def flowise_chat():
    return render_template("flowise_chat.html")

@web_bp.route("/pest_disease")
def pest_disease():
    return render_template("pest_disease.html")

@web_bp.route("/pest_disease_predict", methods=["POST"])
def pest_disease_predict():
    # form should be enctype="multipart/form-data" and file input name="image"
    if "image" not in request.files:
        flash("No file part")
        return redirect(url_for("web.pest_disease"))
    file = request.files["image"]
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("web.pest_disease"))
    try:
        result = predict_disease(file)
    except Exception as e:
        # better error handling for production
        print("🔥 ERROR in predict_disease:", e)
        flash(f"Prediction failed: {str(e)}")
        return redirect(url_for("web.pest_disease"))

    # render result in template (templates/pest_result.html)
    return render_template('pest_result.html',
                       title=result['label'],
                       desc=result['description'],
                       prevent=result['prevention'],
                       image_url=result['image_url'],
                       sname=result['supplement_name'],
                       simage=result['supplement_image_url'],
                       buy_link=result['supplement_buy_link'],
                       probability=round(result['probability'] * 100, 2),
                       saved_path=result['saved_path'],  # should be a URL accessible by browser: e.g. '/static/uploads/xyz.jpg'
                       pred=result['pred_index'])

    
@web_bp.route("/test_form")
def test_form():
    return render_template("test_form.html")

@web_bp.route("/simple_crop_form")
def simple_crop_form():
    return render_template("simple_crop_form.html")

