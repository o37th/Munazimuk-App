from flask import Flask, request, render_template_string, send_file
import re
from datetime import datetime, timedelta
import pytz
import io

app = Flask(__name__)
# HTML Template with updated CSS
html_template = """
<!doctype html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- HTML Meta Tags -->
<title>تطبيق منظمك | الحل الاسهل لي ادارة مواعيدك</title>
<meta name="description" content="تطبيق "منظمك" هو تطبيق متقدم من شركة "أيسكان" مصمم خصيصاً لمساعدة كبار السن في إضافة مواعيدهم إلى التقويم بسهولة وبضغطة زر.">
<!-- Favicon -->
<link rel="icon" href="Fovicon.png" type="image/x-icon">

<!-- Facebook Meta Tags -->
<meta property="og:url" content="https://ceo-iscan.netlify.app">
<meta property="og:type" content="website">
<meta property="og:title" content="تطبيق منظمك | الحل الاسهل لي ادارة مواعيدك">
<meta property="og:description" content="تطبيق "منظمك" هو تطبيق متقدم من شركة "أيسكان" مصمم خصيصاً لمساعدة كبار السن في إضافة مواعيدهم إلى التقويم بسهولة وبضغطة زر.">
<meta property="og:image" content="https://opengraph.b-cdn.net/production/images/59ebbc9c-546b-4824-86d5-6c43add9a047.png?token=PgVqgrR6dBQ52IKh5xRUpQ-TsT3Gb1bGqmIliozpW8c&height=630&width=1200&expires=33267050483">

<!-- Twitter Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta property="twitter:domain" content="ceo-iscan.netlify.app">
<meta property="twitter:url" content="https://ceo-iscan.netlify.app">
<meta name="twitter:title" content="تطبيق منظمك | الحل الاسهل لي ادارة مواعيدك">
<meta name="twitter:description" content="تطبيق "منظمك" هو تطبيق متقدم من شركة "أيسكان" مصمم خصيصاً لمساعدة كبار السن في إضافة مواعيدهم إلى التقويم بسهولة وبضغطة زر.">
<meta name="twitter:image" content="https://opengraph.b-cdn.net/production/images/59ebbc9c-546b-4824-86d5-6c43add9a047.png?token=PgVqgrR6dBQ52IKh5xRUpQ-TsT3Gb1bGqmIliozpW8c&height=630&width=1200&expires=33267050483">

    <style>
        /* CSS for styling the page */
        @font-face {
            font-family: 'SFProAR';
            src: url('/static/fonts/alfont_com_SFProAR_semibold.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }

        body {
            font-family: 'SFProAR', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #edeae9;
            color: #4A4A4A;
            text-align: center;
            padding: 50px 20px;
            direction: rtl;
        }

        h1 {
            color: #333;
            font-size: 36px;
            margin-bottom: 20px;
            font-weight: bold;
        }

        h2 {
            color: #555;
            font-size: 22px;
            margin-top: 0;
            margin-bottom: 40px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-radius: 15px;
        }

        textarea {
            width: 100%;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            resize: vertical;
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 20px;
            background-color: #f0f0f0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'SFProAR', Tahoma, Geneva, Verdana, sans-serif;
        }

        button {
            background-color: #333;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 60px;
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-family: 'SFProAR', Tahoma, Geneva, Verdana, sans-serif;
        }

        button:hover {
            background-color: #555;
        }

        footer {
            margin-top: 40px;
            font-size: 14px;
            color: #888;
        }

        .error {
            color: red;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>تطبيق منظمك</h1>
    <h2> كلمتان خفيفتان على اللسان ثقيلتان في الميزان حبيبتان للرحمن : سبحان الله وبحمده سبحان الله العظيم </h2>
    <div class="container">
        <form action="/generate_ics" method="POST">
            <textarea name="smstext" rows="10" placeholder=" يرجى إدخال نص رسالة الموعد التي استلمتها من وزارة الصحة السعودية... "></textarea><br><br>
            <button type="submit">إضافة إلى التقويم</button>
        </form>
        {% if error_message %}
            <p class="error">{{ error_message }}</p>
        {% endif %}
    </div>
    <footer>
        <p> تطبيق منظمك | جميع الحقوق محفوظة لـشركة  <a href="https://wa.me/966509903532">iScan</a>  </p>
    </footer>
</body>
</html>
"""

# Function to clean the input SMS text
def clean_sms_text(sms):
    sms = sms.strip()
    sms = re.sub(r'[\n\r]+', ' ', sms)
    sms = re.sub(r'\s+', ' ', sms)
    return sms

# Function to detect clinic type based on keywords
def get_clinic_type(clinic_name):
    clinic_keywords = {
        "العلاج الطبيعي": "عيادة العلاج الطبيعي",
        "العيون": "عيادة العيون",
        "الأسنان": "عيادة الأسنان",
        "الإصابات": "عيادة الإصابات",
        "النساء": "عيادة النساء",
        "الأطفال": "عيادة الأطفال",
        "الجراحة": "عيادة الجراحة",
        "الطب العام": "عيادة الطب العام",
        "الأنف والأذن": "عيادة الأنف والأذن",
        "التجميل": "عيادة التجميل",
    }

    for keyword, clinic_type in clinic_keywords.items():
        if keyword in clinic_name:
            return clinic_type

    return None

# Function to convert English day of the week to Arabic
def get_arabic_day(day_of_week):
    arabic_days = {
        "Monday": "الاثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الأحد"
    }
    return arabic_days.get(day_of_week, "غير معروف")

# Function to parse the SMS text and extract appointment details
def parse_sms(sms):
    # Clean the SMS text first
    sms = clean_sms_text(sms)

    # Match patterns for hospital name, clinic name, patient name, date, and time
    hospital_pattern = r"^(.*?)\s*–"  # Extracts the hospital name (before the dash)
    clinic_pattern = r"لدى\s*(.*?)\s*يوم"  # Extracts clinic name (between "لدى" and "يوم")
    
    # Match pattern for patient name (e.g., "يود تذكيركم" or "يود إبلاغكم")
    name_pattern = r"(يود (?:تذكيركم|إبلاغكم))\s*([^،]+)"  # Match either phrase and capture patient name after it
    date_pattern = r"(\d{2}/\d{2}/\d{4})"  # Matches dates like 25/09/2024
    time_pattern = r"(\d{2}[:：]\d{2})\s*(صباحا|مساءا)"  # Matches time like 01:15 مساءا

    # Extract the hospital, clinic, and patient information using regex
    hospital_name = re.search(hospital_pattern, sms)
    clinic_name = re.search(clinic_pattern, sms)
    patient_name = re.search(name_pattern, sms)
    date_match = re.search(date_pattern, sms)
    time_match = re.search(time_pattern, sms)

    if not (hospital_name and clinic_name and patient_name and date_match and time_match):
        return None

    # Extract values from the regex groups and strip leading/trailing spaces
    hospital_name = hospital_name.group(1).strip()
    clinic_name = clinic_name.group(1).strip()
    patient_name = patient_name.group(2).strip()
    date_str = date_match.group(1)
    time_str = time_match.group(1)
    ampm = time_match.group(2)

    # Convert Arabic numbers to English
    arabic_to_english = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    date_str = date_str.translate(arabic_to_english)
    time_str = time_str.translate(arabic_to_english)

    # Adjust the time based on AM/PM format
    hour, minute = map(int, time_str.split(":"))
    if ampm == "مساءا" and hour < 12:
        hour += 12
    elif ampm == "صباحا" and hour == 12:
        hour = 0

    # Create the appointment datetime
    appointment_datetime = datetime.strptime(f"{date_str} {hour}:{minute}", "%d/%m/%Y %H:%M")
    day_of_week = appointment_datetime.strftime("%A")
    day_of_week_arabic = get_arabic_day(day_of_week)

    # Get clinic type (using predefined keywords)
    clinic_type = get_clinic_type(clinic_name)

    return hospital_name, clinic_name, clinic_type, patient_name, appointment_datetime, day_of_week_arabic

# Function to generate the .ics file content
def generate_ics_file(sms):
    parsed_data = parse_sms(sms)
    if parsed_data:
        hospital_name, clinic_name, clinic_type, patient_name, appointment_datetime, day_of_week = parsed_data

        timezone = pytz.timezone("Asia/Riyadh")
        appointment_datetime = timezone.localize(appointment_datetime)

        # Format the ICS file content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{clinic_name} - {patient_name} - {hospital_name}
DTSTART:{appointment_datetime.strftime('%Y%m%dT%H%M%S')}
DTEND:{(appointment_datetime + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')}
LOCATION:{clinic_name}
DESCRIPTION:المريض: {patient_name}\\nالعيادة: {clinic_type}\\nالمستشفى: {hospital_name}\\nالتاريخ: {appointment_datetime.strftime('%d/%m/%Y')}\\nالوقت: {appointment_datetime.strftime('%H:%M')}\\nاليوم: {day_of_week}
BEGIN:VALARM
TRIGGER:-P2D
DESCRIPTION:تذكير قبل 2 يوم
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
DESCRIPTION:تذكير قبل 1 يوم
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-PT30M
DESCRIPTION:تذكير قبل 30 دقيقة
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""

        file_name = f"{patient_name}_{appointment_datetime.strftime('%Y%m%d')}.ics"
        
        # Saving the file in memory and sending it as a download
        response = send_file(
            io.BytesIO(ics_content.encode('utf-8')),
            as_attachment=True,
            download_name=file_name,
            mimetype="text/calendar"
        )
        
        return response
    else:
        return None

@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_template)

@app.route('/generate_ics', methods=['POST'])
def generate_ics():
    sms = request.form['smstext']
    if not sms:
        return render_template_string(html_template, error_message="يرجى إدخال نص الرسالة.")
    
    response = generate_ics_file(sms)
    if response:
        return response
    else:
        return render_template_string(html_template, error_message="لم يتم التعرف على المعلومة من النص المدخل. يرجى التحقق من النص.")

if __name__ == '__main__':
    app.run(debug=True)
