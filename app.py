from flask import Flask, render_template, request
from deepface import DeepFace
import os
import cv2
from werkzeug.utils import secure_filename
from youtubesearchpython import VideosSearch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

emotions_emojis = [
    ("happy", "😊"), ("sad", "😢"), ("angry", "😠"), ("surprised", "😲"), ("neutral", "😐"),
    ("fear", "😱"), ("disgust", "🤢"), ("confused", "😕"), ("love", "❤️"), ("bored", "🥱"),
    ("joy", "😁"), ("shy", "☺️"), ("excited", "🤩"), ("calm", "😌"), ("tired", "😴"),
    ("crying", "😭"), ("silly", "😜"), ("smirk", "😏"), ("pouting", "😡"), ("worried", "😟"),
    ("hopeful", "🤞"), ("embarrassed", "😳"), ("proud", "😌"), ("annoyed", "😒"), ("grateful", "🙏"),
    ("ashamed", "😞"), ("relieved", "😅"), ("in love", "😍"), ("amused", "😄"), ("awkward", "😬"),
    ("peaceful", "🧘"), ("lonely", "🥺"), ("frustrated", "😤"), ("nostalgic", "🫶"), ("nervous", "😬"),
    ("jealous", "😒"), ("content", "😊"), ("inspired", "✨"), ("mischievous", "😈"), ("goofy", "🤪"),
    ("angsty", "😖"), ("flirty", "😘"), ("determined", "💪"), ("suspicious", "🤨"), ("zen", "🧘‍♂️"),
    ("energetic", "⚡"), ("panicked", "😰"), ("skeptical", "🤔"), ("sick", "🤒"), ("drunk", "🍻"),
    # Additional 200 entries
    ("heartbroken", "💔"), ("playful", "🎮"), ("shocked", "😵"), ("dizzy", "🥴"), ("mind blown", "🤯"),
    ("cool", "😎"), ("whistling", "😗"), ("kissing", "😙"), ("winking", "😉"), ("tongue out", "😛"),
    ("drooling", "🤤"), ("sleepy", "😪"), ("cold", "🥶"), ("hot", "🥵"), ("injured", "🤕"),
    ("nauseated", "🤮"), ("sneezing", "🤧"), ("masked", "😷"), ("money eyes", "🤑"), ("cowboy", "🤠"),
    ("clown", "🤡"), ("lying", "🤥"), ("angel", "😇"), ("alien", "👽"), ("robot", "🤖"),
    ("monster", "👹"), ("ghost", "👻"), ("skull", "💀"), ("poo", "💩"), ("smiling devil", "👿"),
    ("imp", "👿"), ("cat happy", "😺"), ("cat sad", "😿"), ("cat kiss", "😽"), ("cat cry", "😿"),
    ("dog", "🐶"), ("fox", "🦊"), ("bear", "🐻"), ("panda", "🐼"), ("tiger", "🐯"),
    ("lion", "🦁"), ("unicorn", "🦄"), ("dragon", "🐲"), ("cactus", "🌵"), ("tree", "🌲"),
    ("sun", "☀️"), ("moon", "🌙"), ("star", "⭐"), ("glowing star", "🌟"), ("shooting star", "🌠"),
    ("cloud", "☁️"), ("rainbow", "🌈"), ("fire", "🔥"), ("water", "💧"), ("wave", "🌊"),
    ("snow", "❄️"), ("snowman", "⛄"), ("wind", "🌬️"), ("tornado", "🌪️"), ("volcano", "🌋"),
    ("earth", "🌍"), ("globe", "🌎"), ("ringed planet", "🪐"), ("rocket", "🚀"), ("flying saucer", "🛸"),
    ("bellhop", "🛎️"), ("door", "🚪"), ("window", "🪟"), ("bed", "🛏️"), ("couch", "🛋️"),
    ("toilet", "🚽"), ("shower", "🚿"), ("bathtub", "🛁"), ("razor", "🪒"), ("lotion", "🧴"),
    ("safety pin", "🧷"), ("broom", "🧹"), ("basket", "🧺"), ("roll of paper", "🧻"), ("soap", "🧼"),
    ("sponge", "🧽"), ("fire extinguisher", "🧯"), ("shopping cart", "🛒"), ("smoking", "🚬"), ("coffin", "⚰️"),
    ("headstone", "🪦"), ("funeral urn", "⚱️"), ("nazar", "🧿"), ("hamsa", "🪬"), ("moai", "🗿"),
    ("placard", "🪧"), ("identification", "🪪"), ("ATM", "🏧"), ("litter", "🚮"), ("potable water", "🚰"),
    ("wheelchair", "♿"), ("men's room", "🚹"), ("women's room", "🚺"), ("restroom", "🚻"), ("baby symbol", "🚼"),
    ("water closet", "🚾"), ("passport control", "🛂"), ("customs", "🛃"), ("baggage claim", "🛄"), ("left luggage", "🛅"),
    ("warning", "⚠️"), ("children crossing", "🚸"), ("no entry", "⛔"), ("prohibited", "🚫"), ("no bicycles", "🚳"),
    ("no smoking", "🚭"), ("no littering", "🚯"), ("non-potable water", "🚱"), ("no pedestrians", "🚷"), ("no mobile phones", "📵"),
    ("underage", "🔞"), ("radioactive", "☢️"), ("biohazard", "☣️"), ("up arrow", "⬆️"), ("down arrow", "⬇️"),
    ("left arrow", "⬅️"), ("right arrow", "➡️"), ("up-right arrow", "↗️"), ("down-right arrow", "↘️"), ("down-left arrow", "↙️"),
    ("up-left arrow", "↖️"), ("up-down arrow", "↕️"), ("left-right arrow", "↔️"), ("right arrow curving left", "↩️"), ("left arrow curving right", "↪️"),
    ("right arrow curving up", "⤴️"), ("right arrow curving down", "⤵️"), ("clockwise arrows", "🔃"), ("counterclockwise arrows", "🔄"), ("BACK arrow", "🔙"),
    ("END arrow", "🔚"), ("ON! arrow", "🔛"), ("SOON arrow", "🔜"), ("TOP arrow", "🔝"), ("place of worship", "🛐"),
    ("atom symbol", "⚛️"), ("om", "🕉️"), ("star of David", "✡️"), ("wheel of dharma", "☸️"), ("yin yang", "☯️"),
    ("latin cross", "✝️"), ("orthodox cross", "☦️"), ("star and crescent", "☪️"), ("peace symbol", "☮️"), ("menorah", "🕎"),
    ("dotted six-pointed star", "🔯"), ("Aries", "♈"), ("Taurus", "♉"), ("Gemini", "♊"), ("Cancer", "♋"),
    ("Leo", "♌"), ("Virgo", "♍"), ("Libra", "♎"), ("Scorpio", "♏"), ("Sagittarius", "♐"),
    ("Capricorn", "♑"), ("Aquarius", "♒"), ("Pisces", "♓"), ("Ophiuchus", "⛎"), ("shuffle tracks", "🔀"),
    ("repeat", "🔁"), ("repeat single", "🔂"), ("play", "▶️"), ("fast-forward", "⏩"), ("next track", "⏭️"),
    ("play/pause", "⏯️"), ("reverse", "◀️"), ("fast reverse", "⏪"), ("last track", "⏮️"), ("upwards button", "🔼"),
    ("fast up", "⏫"), ("downwards button", "🔽"), ("fast down", "⏬"), ("pause", "⏸️"), ("stop", "⏹️"),
    ("record", "⏺️"), ("eject", "⏏️"), ("cinema", "🎦"), ("dim button", "🔅"), ("bright button", "🔆"),
    ("antenna bars", "📶"), ("vibration mode", "📳"), ("mobile phone off", "📴"), ("female sign", "♀️"), ("male sign", "♂️"),
    ("transgender symbol", "⚧️"), ("multiply", "✖️"), ("plus", "➕"), ("minus", "➖"), ("divide", "➗"),
    ("infinity", "♾️"), ("double exclamation", "‼️"), ("exclamation question", "⁉️"), ("red question", "❓"), ("white question", "❔"),
    ("white exclamation", "❕"), ("red exclamation", "❗"), ("wavy dash", "〰️"), ("currency exchange", "💱"), ("heavy dollar", "💲"),
    ("medical symbol", "⚕️"), ("recycling", "♻️"), ("fleur-de-lis", "⚜️"), ("trident", "🔱"), ("name badge", "📛"),
    ("Japanese symbol for beginner", "🔰"), ("hollow red circle", "⭕"), ("check mark", "✅"), ("check box", "☑️"), ("check mark button", "✔️"),
    ("cross mark", "❌"), ("cross mark button", "❎"), ("curly loop", "➰"), ("double curly loop", "➿"), ("part alternation", "〽️"),
    ("eight-spoked asterisk", "✳️"), ("eight-pointed star", "✴️"), ("sparkle", "❇️"), ("copyright", "©️"), ("registered", "®️"),
    ("trade mark", "™️"), ("keycap: #", "#️⃣"), ("keycap: *", "*️⃣"), ("keycap: 0", "0️⃣"), ("keycap: 1", "1️⃣"),
    ("keycap: 2", "2️⃣"), ("keycap: 3", "3️⃣"), ("keycap: 4", "4️⃣"), ("keycap: 5", "5️⃣"), ("keycap: 6", "6️⃣"),
    ("keycap: 7", "7️⃣"), ("keycap: 8", "8️⃣"), ("keycap: 9", "9️⃣"), ("keycap: 10", "🔟"), ("input latin uppercase", "🔠"),
    ("input latin lowercase", "🔡"), ("input numbers", "🔢"), ("input symbols", "🔣"), ("input latin letters", "🔤"), ("A button (blood type)", "🅰️"),
    ("AB button (blood type)", "🆎"), ("B button (blood type)", "🅱️"), ("CL button", "🆑"), ("COOL button", "🆒"), ("FREE button", "🆓"),
    ("information", "ℹ️"), ("ID button", "🆔"), ("circled M", "Ⓜ️"), ("NEW button", "🆕"), ("NG button", "🆖"),
    ("O button (blood type)", "🅾️"), ("OK button", "🆗"), ("P button", "🅿️"), ("SOS button", "🆘"), ("UP! button", "🆙"),
    ("VS button", "🆚"), ("Japanese 'here' button", "🈁"), ("Japanese 'service charge' button", "🈂️"), ("Japanese 'monthly amount' button", "🈷️"), ("Japanese 'not free of charge' button", "🈶")
]

emotion_to_emoji = dict(emotions_emojis)

def get_youtube_links(emotion):
    try:
        search_query = f"{emotion} songs and movies"
        search = VideosSearch(search_query, limit=3)
        return [(video['title'], video['link']) for video in search.result()['result']]
    except Exception as e:
        return [("YouTube Search Failed", str(e))]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        analysis = DeepFace.analyze(img_path=filepath, actions=['emotion'], enforce_detection=False)
        emotion = analysis[0]['dominant_emotion']
        emoji_icon = emotion_to_emoji.get(emotion.lower(), '')
        recommendations = get_youtube_links(emotion)
        return render_template('index.html', image_path=filepath, emotion=emotion,
                               emoji_icon=emoji_icon, recommendations=recommendations)
    except Exception as e:
        return f"Error analyzing image: {e}"

@app.route('/webcam', methods=['POST'])
def webcam():
    cap = cv2.VideoCapture(0)
    cv2.waitKey(2)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Failed to capture image from webcam"

    webcam_path = os.path.join(app.config['UPLOAD_FOLDER'], 'webcam.jpg')
    cv2.imwrite(webcam_path, frame)

    try:
        analysis = DeepFace.analyze(img_path=webcam_path, actions=['emotion'], enforce_detection=False)
        emotion = analysis[0]['dominant_emotion']
        emoji_icon = emotion_to_emoji.get(emotion.lower(), '')
        recommendations = get_youtube_links(emotion)
        return render_template('index.html', image_path=webcam_path, emotion=emotion,
                               emoji_icon=emoji_icon, recommendations=recommendations)
    except Exception as e:
        return f"Error analyzing webcam image: {e}"

if __name__ == '__main__':
    app.run(debug=True)