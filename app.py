from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
import os
from dotenv import load_dotenv
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from gtts import gTTS
import io
import tempfile
import json
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Language code mapping
LANGUAGE_CODES = {
    'english': 'en',
    'spanish': 'es',
    'french': 'fr',
    'german': 'de',
    'italian': 'it',
    'portuguese': 'pt',
    'russian': 'ru',
    'japanese': 'ja',
    'chinese': 'zh',
    'korean': 'ko',
    'arabic': 'ar',
    'hindi': 'hi',
    'dutch': 'nl',
    'swedish': 'sv',
    'polish': 'pl',
    'turkish': 'tr',
    'vietnamese': 'vi',
    'thai': 'th',
    'greek': 'el',
    'czech': 'cs'
}

# Common phrases for different travel types
COMMON_PHRASES = {
    'business': [
        "Hello, nice to meet you",
        "Thank you for your time",
        "Could you please repeat that?",
        "I don't understand",
        "Where is the meeting room?",
        "What time is the meeting?",
        "Could you send me the documents?",
        "I need to make a phone call",
        "Is there Wi-Fi available?",
        "Could you recommend a good restaurant?",
        "How do I get to the office?",
        "I need to check my email",
        "Could you help me with this?",
        "What is the password for the Wi-Fi?",
        "I need to print some documents",
        "Could we schedule a follow-up meeting?",
        "What are the business hours?",
        "Is there a business center nearby?",
        "Could you explain the local business customs?",
        "Where can I find a translator?",
        "What's the dress code for meetings?",
        "Could you recommend a good hotel for business travelers?",
        "Is there a quiet place to make a video call?",
        "What's the best way to exchange business cards?",
        "Could you help me understand the local business etiquette?"
    ],
    'leisure': [
        "Hello, how are you?",
        "Thank you very much",
        "Could you help me?",
        "Where is the bathroom?",
        "How much does this cost?",
        "I would like to order food",
        "Where is the nearest hotel?",
        "Could you take a photo of us?",
        "What time does it open?",
        "Is there a discount?",
        "Where can I buy tickets?",
        "Which way to the beach?",
        "I'm lost, can you help?",
        "What do you recommend?",
        "Is this the right way?",
        "Could you recommend a local restaurant?",
        "What are the must-see attractions?",
        "Is there a guided tour available?",
        "Where can I rent a bicycle?",
        "What's the best time to visit?",
        "Are there any local festivals happening?",
        "Could you suggest some shopping areas?",
        "What's the local specialty food?",
        "Is there a night market nearby?",
        "Where can I watch the sunset?"
    ],
    'emergency': [
        "Help!",
        "Call an ambulance",
        "I need a doctor",
        "Where is the hospital?",
        "I'm lost",
        "I need the police",
        "This is an emergency",
        "I've lost my passport",
        "My wallet was stolen",
        "I need to contact my embassy",
        "Is there a pharmacy nearby?",
        "I'm not feeling well",
        "I need to call home",
        "Where is the police station?",
        "I need to report a crime",
        "I need emergency medical assistance",
        "Where is the nearest emergency room?",
        "I've had an accident",
        "I need to contact my insurance company",
        "Is there a 24-hour clinic nearby?",
        "I need to cancel my travel plans",
        "Where can I get emergency cash?",
        "I need to contact my family",
        "Is there a consulate nearby?",
        "I need to file a police report"
    ],
    'backpacking': [
        "Hello, do you speak English?",
        "How much is a bed in the dorm?",
        "Is breakfast included?",
        "Where is the bus station?",
        "What time does the bus leave?",
        "Is there a laundry service?",
        "Can I leave my bag here?",
        "Where can I get water?",
        "Is it safe to walk here at night?",
        "What's the Wi-Fi password?",
        "Do you have a map?",
        "Where can I buy a SIM card?",
        "Is there a supermarket nearby?",
        "What's the best way to get to...?",
        "Can I use my credit card here?",
        "Where can I find cheap local food?",
        "Is there a free walking tour?",
        "What's the best hiking trail?",
        "Where can I camp safely?",
        "Is there a local market today?",
        "What's the best way to meet other travelers?",
        "Where can I get my clothes washed?",
        "Is there a place to store my luggage?",
        "What's the local transportation like?",
        "Where can I find a good view of the city?"
    ],
    'romantic': [
        "You are beautiful",
        "I love you",
        "Will you marry me?",
        "You make me happy",
        "I miss you",
        "You are special to me",
        "I want to be with you",
        "You are my everything",
        "I can't live without you",
        "You are my dream come true",
        "I want to spend my life with you",
        "You are my soulmate",
        "I love your smile",
        "You are perfect",
        "I want to hold your hand forever",
        "You make my heart skip a beat",
        "I love the way you look at me",
        "You are the most beautiful person I know",
        "I want to dance with you",
        "You are my favorite person",
        "I love spending time with you",
        "You make every moment special",
        "I want to kiss you",
        "You are my inspiration",
        "I love your laugh"
    ],
    'festival': [
        "When does the festival start?",
        "Where is the main stage?",
        "What time is the parade?",
        "Is there an entrance fee?",
        "Where can I buy festival tickets?",
        "What are the festival highlights?",
        "Is there a festival map?",
        "Where can I find traditional costumes?",
        "What are the festival traditions?",
        "Is there a special festival food?",
        "Where can I watch the performances?",
        "What time do the celebrations end?",
        "Is there a festival program?",
        "Where can I buy festival souvenirs?",
        "What are the festival customs?",
        "Is there a cultural show?",
        "Where can I learn the traditional dance?",
        "What's the festival history?",
        "Is there a fireworks display?",
        "Where can I find festival decorations?",
        "What are the festival rules?",
        "Is there a special ceremony?",
        "Where can I take festival photos?",
        "What's the festival significance?",
        "Is there a traditional blessing?"
    ],
    'study_abroad': [
        "Where is the university?",
        "What are the class hours?",
        "Is there a student discount?",
        "Where is the library?",
        "What's the Wi-Fi password?",
        "Is there a student center?",
        "Where can I buy textbooks?",
        "What are the office hours?",
        "Is there a language exchange program?",
        "Where is the computer lab?",
        "What's the deadline for assignments?",
        "Is there a student housing office?",
        "Where can I find study groups?",
        "What are the campus facilities?",
        "Is there a student ID card?",
        "Where is the international student office?",
        "What are the academic requirements?",
        "Is there a campus tour?",
        "Where can I get a student visa?",
        "What's the grading system?",
        "Is there a student health center?",
        "Where can I find academic advisors?",
        "What are the course registration dates?",
        "Is there a student discount for transportation?",
        "Where can I get a student bank account?"
    ],
    'medical_travel': [
        "I have a medical appointment",
        "Where is the hospital?",
        "I need to see a doctor",
        "What are the visiting hours?",
        "I need to fill a prescription",
        "Where is the pharmacy?",
        "I have a medical emergency",
        "What are the hospital facilities?",
        "I need to make a follow-up appointment",
        "Where is the specialist's office?",
        "I need to get a medical test",
        "What are the insurance requirements?",
        "I need to contact my doctor",
        "Where is the medical records office?",
        "I need to get a second opinion",
        "What are the treatment options?",
        "I need to schedule surgery",
        "Where is the recovery room?",
        "I need to get a medical certificate",
        "What are the post-treatment instructions?",
        "I need to find a medical translator",
        "Where is the patient information desk?",
        "I need to get a medical visa",
        "What are the hospital policies?",
        "I need to arrange medical transportation"
    ],
    'diplomacy': [
        "I need to contact my embassy",
        "Where is the consulate?",
        "I need to renew my passport",
        "What are the visa requirements?",
        "I need to schedule an appointment",
        "Where is the diplomatic mission?",
        "I need to get official documents",
        "What are the diplomatic protocols?",
        "I need to meet with officials",
        "Where is the protocol office?",
        "I need to arrange a diplomatic meeting",
        "What are the security procedures?",
        "I need to get diplomatic clearance",
        "Where is the diplomatic corps office?",
        "I need to file official paperwork",
        "What are the diplomatic privileges?",
        "I need to contact the ambassador",
        "Where is the diplomatic residence?",
        "I need to arrange official transportation",
        "What are the diplomatic customs?",
        "I need to get diplomatic accreditation",
        "Where is the diplomatic mail office?",
        "I need to schedule a diplomatic event",
        "What are the diplomatic immunities?",
        "I need to contact the foreign ministry"
    ],
    'trade': [
        "I'm here for a business meeting",
        "Where is the trade center?",
        "I need to meet with suppliers",
        "What are the business hours?",
        "I need to arrange a factory visit",
        "Where is the industrial zone?",
        "I need to discuss pricing",
        "What are the payment terms?",
        "I need to inspect the products",
        "Where is the shipping office?",
        "I need to negotiate a contract",
        "What are the import regulations?",
        "I need to meet with distributors",
        "Where is the trade fair?",
        "I need to discuss logistics",
        "What are the export requirements?",
        "I need to arrange a business lunch",
        "Where is the business district?",
        "I need to discuss quality control",
        "What are the trade agreements?",
        "I need to meet with manufacturers",
        "Where is the customs office?",
        "I need to discuss delivery terms",
        "What are the business customs?",
        "I need to arrange a business dinner"
    ]
}

REAL_LIFE_SCENARIOS = {
    "dining": {
        "icon": "🍽️",
        "title": "Dining & Restaurant",
        "phrases": [
            "I am vegetarian.",
            "No onions, please.",
            "What is this dish?",
            "Is it spicy?",
            "Does this contain nuts?",
            "Can I get some water?",
            "Ketchup, please.",
            "Can we get separate checks?",
            "Is tipping included?",
            "How much should I tip?",
            "Do you have a table for two at 8 PM?",
            "Can I get this to-go?"
        ]
    },
    "hotel": {
        "icon": "🏨",
        "title": "Hotel & Accommodation",
        "phrases": [
            "I would like to check in.",
            "I would like to check out.",
            "Can I get the Wi-Fi password?",
            "Can I have more towels?",
            "Can I get some water?",
            "Can you turn on the air conditioning?",
            "I would like room service.",
            "Can I get a wake-up call?"
        ]
    },
    "transport": {
        "icon": "🚕",
        "title": "Transportation",
        "phrases": [
            "Please take me to this address.",
            "What time does the bus leave?",
            "What time does the train leave?",
            "Where can I buy tickets?",
            "Stop here, please."
        ]
    },
    "shopping": {
        "icon": "🛍️",
        "title": "Shopping & Markets",
        "phrases": [
            "How much does this cost?",
            "Can you give me a discount?",
            "I'm just looking, thank you.",
            "Do you have this in another size?",
            "Do you have this in another color?"
        ]
    },
    "emergency": {
        "icon": "🚨",
        "title": "Emergency & Help",
        "phrases": [
            "Call the police!",
            "I've lost my passport.",
            "I need a doctor.",
            "Where is the nearest pharmacy?"
        ]
    },
    "navigation": {
        "icon": "🗺️",
        "title": "Navigation / Sightseeing",
        "phrases": [
            "How do I get to this place?",
            "Where is the restroom?",
            "Can I take photos here?"
        ]
    },
    "social": {
        "icon": "🤝",
        "title": "Social & Greeting",
        "phrases": [
            "Nice to meet you.",
            "Do you speak English?",
            "I'm learning this language."
        ]
    }
}

def get_language_code(language):
    """Convert language name to language code"""
    language = language.lower().strip()
    return LANGUAGE_CODES.get(language, language)

def translate_text(text, source_lang, target_lang):
    """Translate text using MyMemory API"""
    try:
        # Convert language names to codes
        source_code = get_language_code(source_lang)
        target_code = get_language_code(target_lang)
        
        # MyMemory API endpoint
        url = f"https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": f"{source_code}|{target_code}"
        }
        
        # Reduce API calls delay to minimize timeout risk
        time.sleep(0.2)  # Reduced from 0.5

        # Add timeout to the request to prevent hanging
        response = requests.get(url, params=params, timeout=5)
        print(f"Translation API Response: {response.status_code} - {response.text}")  # Debug print
        
        if response.status_code == 200:
            data = response.json()
            if data.get("responseStatus") == 200:
                return data["responseData"]["translatedText"]
            else:
                print(f"Translation API Error: {data.get('responseDetails', 'Unknown error')}")
                return f"[Translation unavailable: {text}]"  # Return a fallback instead of None
        else:
            print(f"Translation API Error: Status code {response.status_code}")
            return f"[Translation error: {text}]"  # Return a fallback instead of None
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return f"[Error: {text}]"  # Return a fallback instead of None
def get_pronunciation_guide(text, target_lang):
    """Generate a simple pronunciation guide"""
    try:
        # Get language code for gTTS
        lang_code = get_language_code(target_lang)
        return f"Listen to pronunciation by clicking the speaker icon"
    except Exception as e:
        print(f"Pronunciation guide error: {str(e)}")
        return "Pronunciation guide not available"

def generate_phrases(native_lang, target_lang, travel_type):
    try:
        print(f"Generating phrases for: {native_lang} -> {target_lang}, type: {travel_type}")  # Debug print
        
        # Limit the number of phrases to prevent timeout
        phrases_to_translate = COMMON_PHRASES[travel_type][:10]  # Only translate 10 phrases

        phrases = []
        for phrase in phrases_to_translate:
            print(f"Translating: {phrase}")  # Debug print
            translated = translate_text(phrase, native_lang, target_lang)
            
            if translated:
                print(f"Translated to: {translated}")  # Debug print
                pronunciation = get_pronunciation_guide(translated, target_lang)
                phrases.append({
                    'native_phrase': phrase,
                    'target_phrase': translated,
                    'pronunciation': pronunciation
                })
            else:
                print(f"Translation failed for: {phrase}")  # Debug print
        
        if phrases:
            print(f"Successfully generated {len(phrases)} phrases")  # Debug print
            return phrases
        else:
            error_msg = "Could not generate any translations. Please check your language inputs and try again."
            print(error_msg)  # Debug print
            flash(error_msg, "danger")
            return None
            
    except Exception as e:
        error_msg = f"Error generating phrases: {str(e)}"
        print(error_msg)  # Debug print
        flash(error_msg, "danger")
        return None

class CheatSheetForm(FlaskForm):
    native_language = SelectField('Native Language', 
                            choices=[
                                ('en', 'English'),
                                ('es', 'Spanish'),
                                ('fr', 'French'),
                                ('de', 'German'),
                                ('it', 'Italian'),
                                ('pt', 'Portuguese'),
                                ('ru', 'Russian'),
                                ('ja', 'Japanese'),
                                ('zh', 'Chinese'),
                                ('ko', 'Korean'),
                                ('ar', 'Arabic'),
                                ('hi', 'Hindi'),
                                ('nl', 'Dutch'),
                                ('sv', 'Swedish'),
                                ('pl', 'Polish'),
                                ('tr', 'Turkish'),
                                ('vi', 'Vietnamese'),
                                ('th', 'Thai'),
                                ('el', 'Greek'),
                                ('cs', 'Czech')
                            ],
                            validators=[DataRequired()])
    target_language = SelectField('Target Language', 
                            choices=[
                                ('en', 'English'),
                                ('es', 'Spanish'),
                                ('fr', 'French'),
                                ('de', 'German'),
                                ('it', 'Italian'),
                                ('pt', 'Portuguese'),
                                ('ru', 'Russian'),
                                ('ja', 'Japanese'),
                                ('zh', 'Chinese'),
                                ('ko', 'Korean'),
                                ('ar', 'Arabic'),
                                ('hi', 'Hindi'),
                                ('nl', 'Dutch'),
                                ('sv', 'Swedish'),
                                ('pl', 'Polish'),
                                ('tr', 'Turkish'),
                                ('vi', 'Vietnamese'),
                                ('th', 'Thai'),
                                ('el', 'Greek'),
                                ('cs', 'Czech')
                            ],
                            validators=[DataRequired()])
    travel_type = SelectField('Travel Type', 
                            choices=[
                                ('business', 'Business'),
                                ('leisure', 'Leisure'),
                                ('emergency', 'Emergency'),
                                ('backpacking', 'Backpacking'),
                                ('romantic', 'Romantic'),
                                ('festival', 'Festival'),
                                ('study_abroad', 'Study Abroad'),
                                ('medical_travel', 'Medical Travel'),
                                ('diplomacy', 'Diplomacy'),
                                ('trade', 'Trade')
                            ],
                            validators=[DataRequired()])
    submit = SubmitField('Generate Cheat Sheet')

def create_pdf(phrases, native_lang, target_lang):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Travel Cheat Sheet: {native_lang} to {target_lang}")
    
    # Add phrases
    p.setFont("Helvetica", 12)
    y = height - 100
    for phrase in phrases:
        p.drawString(50, y, f"Native ({native_lang}): {phrase['native_phrase']}")
        y -= 20
        p.drawString(50, y, f"Target ({target_lang}): {phrase['target_phrase']}")
        y -= 20
        p.drawString(50, y, f"Pronunciation: {phrase['pronunciation']}")
        y -= 30
        
        if y < 50:  # Start new page if running out of space
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)
    
    p.save()
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CheatSheetForm()
    if form.validate_on_submit():
        try:
            phrases = generate_phrases(
                form.native_language.data,
                form.target_language.data,
                form.travel_type.data
            )
            if phrases:
                return render_template('result.html', 
                                     phrases=phrases,
                                     native_lang=form.native_language.data,
                                     target_lang=form.target_language.data)
            else:
                flash("Failed to generate phrases. Please try again.", "danger")
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('index'))
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")
    return render_template('index.html', form=form)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    phrases = data['phrases']
    native_lang = data['native_lang']
    target_lang = data['target_lang']
    
    pdf_buffer = create_pdf(phrases, native_lang, target_lang)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'travel_cheat_sheet_{native_lang}_to_{target_lang}.pdf'
    )

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        if not data or 'text' not in data or 'lang' not in data:
            return jsonify({'error': 'Missing text or language parameter'}), 400

        text = data['text']
        lang = get_language_code(data['lang'])  # Convert language name to code
        
        # Limit text length to prevent timeout
        if len(text) > 200:
            text = text[:200] + "..."

        print(f"Generating audio for: {text} in language: {lang}")  # Debug print
        
        # Create a temporary file with a unique name
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        temp_file.close()
        
        try:
            # Generate speech with a timeout
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_filename)
            
            # Send the file
            response = send_file(
                temp_filename,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='pronunciation.mp3'
            )
            
            # Add cleanup callback
            @response.call_on_close
            def cleanup():
                try:
                    os.unlink(temp_filename)
                except Exception as e:
                    print(f"Error cleaning up temp file: {e}")
            
            return response
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            # Clean up temp file if it exists
            try:
                os.unlink(temp_filename)
            except:
                pass
            return jsonify({'error': f'Error generating audio: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Error in generate_audio route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/real-life-scenarios', methods=['GET', 'POST'])
def real_life_scenarios():
    form = ScenarioLanguageForm()
    scenarios = None
    native_lang = None
    target_lang = None
    if form.validate_on_submit():
        native_lang = form.native_language.data
        target_lang = form.target_language.data
        scenarios = {}
        for key, scenario in REAL_LIFE_SCENARIOS.items():
            phrases = []
            # Limit phrases to prevent timeout
            limited_phrases = scenario['phrases'][:5]  # Only translate 5 phrases per scenario
            for phrase in limited_phrases:
                # Native phrase (in native language)
                native_phrase = translate_text(phrase, 'en', native_lang) if native_lang != 'en' else phrase
                # Translated phrase (in target language)
                translated_phrase = translate_text(phrase, 'en', target_lang) if target_lang != 'en' else phrase
                phrases.append({
                    'native': native_phrase,
                    'translation': translated_phrase
                })
            scenarios[key] = {
                'icon': scenario['icon'],
                'title': scenario['title'],
                'phrases': phrases
            }
    return render_template('real_life_scenarios.html', form=form, scenarios=scenarios, native_lang=native_lang, target_lang=target_lang)

class ScenarioLanguageForm(FlaskForm):
    native_language = SelectField('Native Language', 
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('ja', 'Japanese'),
            ('zh', 'Chinese'),
            ('ko', 'Korean'),
            ('ar', 'Arabic'),
            ('hi', 'Hindi'),
            ('nl', 'Dutch'),
            ('sv', 'Swedish'),
            ('pl', 'Polish'),
            ('tr', 'Turkish'),
            ('vi', 'Vietnamese'),
            ('th', 'Thai'),
            ('el', 'Greek'),
            ('cs', 'Czech')
        ],
        validators=[DataRequired()])
    target_language = SelectField('Target Language', 
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('ja', 'Japanese'),
            ('zh', 'Chinese'),
            ('ko', 'Korean'),
            ('ar', 'Arabic'),
            ('hi', 'Hindi'),
            ('nl', 'Dutch'),
            ('sv', 'Swedish'),
            ('pl', 'Polish'),
            ('tr', 'Turkish'),
            ('vi', 'Vietnamese'),
            ('th', 'Thai'),
            ('el', 'Greek'),
            ('cs', 'Czech')
        ],
        validators=[DataRequired()])

if __name__ == '__main__':
    app.run(debug=True,port=5002) 
