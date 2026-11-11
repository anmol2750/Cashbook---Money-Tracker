"""Write the maintained core UI translations for supported Indian locales."""
import json
from pathlib import Path


TRANSLATIONS = {
    "as": {
        "WORKSPACE": "কৰ্মক্ষেত্ৰ", "Overview": "সাৰাংশ", "Transactions": "লেনদেন", "Notes": "টোকা",
        "Calendar": "পঞ্জিকা", "Cash calculator": "নগদ গণক", "PREFERENCES": "পছন্দসমূহ", "Settings": "ছেটিংছ", "About": "বিষয়ে", "About Cashbook": "কেছবুকৰ বিষয়ে",
        "Sign out": "ছাইন আউট", "Profile": "প্ৰ'ফাইল", "Language": "ভাষা",
        "Choose the language used across your cashbook.": "আপোনাৰ কেছবুকত ব্যৱহৃত ভাষা বাছনি কৰক।",
        "Display language": "প্ৰদৰ্শনৰ ভাষা", "Save language": "ভাষা সংৰক্ষণ কৰক", "Cash in": "নগদ জমা",
        "Cash out": "নগদ খৰচ", "Daily": "দৈনিক", "Weekly": "সাপ্তাহিক", "Monthly": "মাহেকীয়া",
        "Yearly": "বাৰ্ষিক", "Apply": "প্ৰয়োগ কৰক", "Clear": "পৰিষ্কাৰ কৰক", "Cancel": "বাতিল",
        "Add transaction": "লেনদেন যোগ কৰক", "Save transaction": "লেনদেন সংৰক্ষণ কৰক", "Amount": "পৰিমাণ",
        "Category": "শ্ৰেণী", "Description": "বিৱৰণ", "Date": "তাৰিখ",
    },
    "bn": {
        "WORKSPACE": "কর্মক্ষেত্র", "Overview": "সারসংক্ষেপ", "Transactions": "লেনদেন", "Notes": "নোট",
        "Calendar": "ক্যালেন্ডার", "Cash calculator": "নগদ ক্যালকুলেটর", "PREFERENCES": "পছন্দসমূহ", "Settings": "সেটিংস", "About": "সম্পর্কে", "About Cashbook": "ক্যাশবুক সম্পর্কে",
        "Sign out": "সাইন আউট", "Profile": "প্রোফাইল", "Language": "ভাষা",
        "Choose the language used across your cashbook.": "আপনার ক্যাশবুকে ব্যবহৃত ভাষা নির্বাচন করুন।",
        "Display language": "প্রদর্শনের ভাষা", "Save language": "ভাষা সংরক্ষণ করুন", "Cash in": "নগদ জমা",
        "Cash out": "নগদ খরচ", "Daily": "দৈনিক", "Weekly": "সাপ্তাহিক", "Monthly": "মাসিক",
        "Yearly": "বার্ষিক", "Apply": "প্রয়োগ করুন", "Clear": "মুছুন", "Cancel": "বাতিল",
        "Add transaction": "লেনদেন যোগ করুন", "Save transaction": "লেনদেন সংরক্ষণ করুন", "Amount": "পরিমাণ",
        "Category": "বিভাগ", "Description": "বিবরণ", "Date": "তারিখ",
    },
    "gu": {
        "WORKSPACE": "કાર્યસ્થળ", "Overview": "ઝાંખી", "Transactions": "વ્યવહારો", "Notes": "નોંધો",
        "Calendar": "કૅલેન્ડર", "Cash calculator": "રોકડ ગણક", "PREFERENCES": "પસંદગીઓ", "Settings": "સેટિંગ્સ", "About": "વિશે", "About Cashbook": "કેશબુક વિશે",
        "Sign out": "સાઇન આઉટ", "Profile": "પ્રોફાઇલ", "Language": "ભાષા",
        "Choose the language used across your cashbook.": "તમારી કેશબુકમાં વપરાતી ભાષા પસંદ કરો.",
        "Display language": "પ્રદર્શન ભાષા", "Save language": "ભાષા સાચવો", "Cash in": "રોકડ આવક",
        "Cash out": "રોકડ જાવક", "Daily": "દૈનિક", "Weekly": "સાપ્તાહિક", "Monthly": "માસિક",
        "Yearly": "વાર્ષિક", "Apply": "લાગુ કરો", "Clear": "સાફ કરો", "Cancel": "રદ કરો",
        "Add transaction": "વ્યવહાર ઉમેરો", "Save transaction": "વ્યવહાર સાચવો", "Amount": "રકમ",
        "Category": "શ્રેણી", "Description": "વર્ણન", "Date": "તારીખ",
    },
    "kn": {
        "WORKSPACE": "ಕಾರ್ಯಕ್ಷೇತ್ರ", "Overview": "ಅವಲೋಕನ", "Transactions": "ವಹಿವಾಟುಗಳು", "Notes": "ಟಿಪ್ಪಣಿಗಳು",
        "Calendar": "ಕ್ಯಾಲೆಂಡರ್", "Cash calculator": "ನಗದು ಕ್ಯಾಲ್ಕುಲೇಟರ್", "PREFERENCES": "ಆದ್ಯತೆಗಳು", "Settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು", "About": "ಬಗ್ಗೆ", "About Cashbook": "ಕ್ಯಾಶ್‌ಬುಕ್ ಬಗ್ಗೆ",
        "Sign out": "ಸೈನ್ ಔಟ್", "Profile": "ಪ್ರೊಫೈಲ್", "Language": "ಭಾಷೆ",
        "Choose the language used across your cashbook.": "ನಿಮ್ಮ ಕ್ಯಾಶ್‌ಬುಕ್‌ನಲ್ಲಿ ಬಳಸುವ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
        "Display language": "ಪ್ರದರ್ಶನ ಭಾಷೆ", "Save language": "ಭಾಷೆಯನ್ನು ಉಳಿಸಿ", "Cash in": "ನಗದು ಜಮೆ",
        "Cash out": "ನಗದು ಖರ್ಚು", "Daily": "ದೈನಿಕ", "Weekly": "ಸಾಪ್ತಾಹಿಕ", "Monthly": "ಮಾಸಿಕ",
        "Yearly": "ವಾರ್ಷಿಕ", "Apply": "ಅನ್ವಯಿಸಿ", "Clear": "ಅಳಿಸಿ", "Cancel": "ರದ್ದುಮಾಡಿ",
        "Add transaction": "ವಹಿವಾಟು ಸೇರಿಸಿ", "Save transaction": "ವಹಿವಾಟನ್ನು ಉಳಿಸಿ", "Amount": "ಮೊತ್ತ",
        "Category": "ವರ್ಗ", "Description": "ವಿವರಣೆ", "Date": "ದಿನಾಂಕ",
    },
    "ks": {
        "WORKSPACE": "کامہٕ کٲم", "Overview": "خلاصہ", "Transactions": "لین دین", "Notes": "نوٹس",
        "Calendar": "کیلنڈر", "Cash calculator": "نقد کیلکولیٹر", "PREFERENCES": "ترجیحات", "Settings": "ترتیبات", "About": "متعلق", "About Cashbook": "کیش بُک کے بارے میں",
        "Sign out": "سائن آؤٹ", "Profile": "پروفائل", "Language": "زبان",
        "Choose the language used across your cashbook.": "پنٛنہِ کیش بُک منز استعمال گژھن وٲلی زبان ژٲریو۔",
        "Display language": "دکھاون وٲلۍ زبان", "Save language": "زبان محفوظ کٔریو", "Cash in": "رقم جمع",
        "Cash out": "رقم خرچ", "Daily": "روزانہ", "Weekly": "ہفتہ وار", "Monthly": "ماہانہ",
        "Yearly": "سالانہ", "Apply": "لاگو کٔریو", "Clear": "صاف کٔریو", "Cancel": "منسوخ",
        "Add transaction": "لین دین شامل کٔریو", "Save transaction": "لین دین محفوظ کٔریو", "Amount": "رقم",
        "Category": "قسم", "Description": "تفصیل", "Date": "تاریخ",
    },
    "ml": {
        "WORKSPACE": "പ്രവർത്തനമേഖല", "Overview": "അവലോകനം", "Transactions": "ഇടപാടുകൾ", "Notes": "കുറിപ്പുകൾ",
        "Calendar": "കലണ്ടർ", "Cash calculator": "ക്യാഷ് കാൽക്കുലേറ്റർ", "PREFERENCES": "മുൻഗണനകൾ", "Settings": "ക്രമീകരണങ്ങൾ", "About": "വിവരം", "About Cashbook": "ക്യാഷ്ബുക്കിനെക്കുറിച്ച്",
        "Sign out": "പുറത്തുകടക്കുക", "Profile": "പ്രൊഫൈൽ", "Language": "ഭാഷ",
        "Choose the language used across your cashbook.": "നിങ്ങളുടെ ക്യാഷ്ബുക്കിൽ ഉപയോഗിക്കേണ്ട ഭാഷ തിരഞ്ഞെടുക്കുക.",
        "Display language": "പ്രദർശന ഭാഷ", "Save language": "ഭാഷ സംരക്ഷിക്കുക", "Cash in": "പണം വരവ്",
        "Cash out": "പണം ചെലവ്", "Daily": "ദിവസേന", "Weekly": "പ്രതിവാരം", "Monthly": "പ്രതിമാസം",
        "Yearly": "വർഷംതോറും", "Apply": "പ്രയോഗിക്കുക", "Clear": "മായ്ക്കുക", "Cancel": "റദ്ദാക്കുക",
        "Add transaction": "ഇടപാട് ചേർക്കുക", "Save transaction": "ഇടപാട് സംരക്ഷിക്കുക", "Amount": "തുക",
        "Category": "വിഭാഗം", "Description": "വിവരണം", "Date": "തീയതി",
    },
    "mr": {
        "WORKSPACE": "कार्य क्षेत्र", "Overview": "आढावा", "Transactions": "व्यवहार", "Notes": "नोंदी",
        "Calendar": "दिनदर्शिका", "Cash calculator": "रोख मोजणी", "PREFERENCES": "प्राधान्ये", "Settings": "सेटिंग्ज", "About": "बद्दल", "About Cashbook": "कॅशबुकबद्दल",
        "Sign out": "साइन आउट", "Profile": "प्रोफाइल", "Language": "भाषा",
        "Choose the language used across your cashbook.": "तुमच्या कॅशबुकमध्ये वापरली जाणारी भाषा निवडा.",
        "Display language": "प्रदर्शन भाषा", "Save language": "भाषा जतन करा", "Cash in": "रोख जमा",
        "Cash out": "रोख खर्च", "Daily": "दैनिक", "Weekly": "साप्ताहिक", "Monthly": "मासिक",
        "Yearly": "वार्षिक", "Apply": "लागू करा", "Clear": "पुसून टाका", "Cancel": "रद्द करा",
        "Add transaction": "व्यवहार जोडा", "Save transaction": "व्यवहार जतन करा", "Amount": "रक्कम",
        "Category": "प्रकार", "Description": "तपशील", "Date": "तारीख",
    },
    "ne": {
        "WORKSPACE": "कार्यस्थल", "Overview": "अवलोकन", "Transactions": "कारोबार", "Notes": "टिपोट",
        "Calendar": "पात्रो", "Cash calculator": "नगद क्याल्कुलेटर", "PREFERENCES": "प्राथमिकताहरू", "Settings": "सेटिङहरू", "About": "बारेमा", "About Cashbook": "क्यासबुकको बारेमा",
        "Sign out": "साइन आउट", "Profile": "प्रोफाइल", "Language": "भाषा",
        "Choose the language used across your cashbook.": "आफ्नो क्यासबुकमा प्रयोग हुने भाषा छान्नुहोस्।",
        "Display language": "प्रदर्शन भाषा", "Save language": "भाषा सुरक्षित गर्नुहोस्", "Cash in": "नगद आम्दानी",
        "Cash out": "नगद खर्च", "Daily": "दैनिक", "Weekly": "साप्ताहिक", "Monthly": "मासिक",
        "Yearly": "वार्षिक", "Apply": "लागू गर्नुहोस्", "Clear": "हटाउनुहोस्", "Cancel": "रद्द गर्नुहोस्",
        "Add transaction": "कारोबार थप्नुहोस्", "Save transaction": "कारोबार सुरक्षित गर्नुहोस्", "Amount": "रकम",
        "Category": "श्रेणी", "Description": "विवरण", "Date": "मिति",
    },
    "or": {
        "WORKSPACE": "କାର୍ଯ୍ୟକ୍ଷେତ୍ର", "Overview": "ସାରାଂଶ", "Transactions": "କାରବାର", "Notes": "ଟିପ୍ପଣୀ",
        "Calendar": "କ୍ୟାଲେଣ୍ଡର", "Cash calculator": "ନଗଦ ଗଣକ", "PREFERENCES": "ପସନ୍ଦ", "Settings": "ସେଟିଂସ୍", "About": "ବିଷୟରେ", "About Cashbook": "କ୍ୟାଶବୁକ୍ ବିଷୟରେ",
        "Sign out": "ସାଇନ୍ ଆଉଟ୍", "Profile": "ପ୍ରୋଫାଇଲ୍", "Language": "ଭାଷା",
        "Choose the language used across your cashbook.": "ଆପଣଙ୍କ କ୍ୟାଶବୁକ୍‌ରେ ବ୍ୟବହୃତ ଭାଷା ବାଛନ୍ତୁ।",
        "Display language": "ପ୍ରଦର୍ଶନ ଭାଷା", "Save language": "ଭାଷା ସଂରକ୍ଷଣ କରନ୍ତୁ", "Cash in": "ନଗଦ ଜମା",
        "Cash out": "ନଗଦ ଖର୍ଚ୍ଚ", "Daily": "ଦୈନିକ", "Weekly": "ସାପ୍ତାହିକ", "Monthly": "ମାସିକ",
        "Yearly": "ବାର୍ଷିକ", "Apply": "ପ୍ରୟୋଗ କରନ୍ତୁ", "Clear": "ସଫା କରନ୍ତୁ", "Cancel": "ବାତିଲ୍",
        "Add transaction": "କାରବାର ଯୋଡ଼ନ୍ତୁ", "Save transaction": "କାରବାର ସଂରକ୍ଷଣ କରନ୍ତୁ", "Amount": "ରାଶି",
        "Category": "ବର୍ଗ", "Description": "ବିବରଣୀ", "Date": "ତାରିଖ",
    },
    "pa": {
        "WORKSPACE": "ਕਾਰਜ-ਖੇਤਰ", "Overview": "ਸੰਖੇਪ", "Transactions": "ਲੈਣ-ਦੇਣ", "Notes": "ਨੋਟਸ",
        "Calendar": "ਕੈਲੰਡਰ", "Cash calculator": "ਨਕਦੀ ਕੈਲਕੁਲੇਟਰ", "PREFERENCES": "ਤਰਜੀਹਾਂ", "Settings": "ਸੈਟਿੰਗਾਂ", "About": "ਬਾਰੇ", "About Cashbook": "ਕੈਸ਼ਬੁੱਕ ਬਾਰੇ",
        "Sign out": "ਸਾਈਨ ਆਉਟ", "Profile": "ਪ੍ਰੋਫ਼ਾਈਲ", "Language": "ਭਾਸ਼ਾ",
        "Choose the language used across your cashbook.": "ਆਪਣੀ ਕੈਸ਼ਬੁੱਕ ਵਿੱਚ ਵਰਤੀ ਜਾਣ ਵਾਲੀ ਭਾਸ਼ਾ ਚੁਣੋ।",
        "Display language": "ਦਿਖਾਉਣ ਦੀ ਭਾਸ਼ਾ", "Save language": "ਭਾਸ਼ਾ ਸੰਭਾਲੋ", "Cash in": "ਨਕਦੀ ਜਮ੍ਹਾਂ",
        "Cash out": "ਨਕਦੀ ਖਰਚ", "Daily": "ਰੋਜ਼ਾਨਾ", "Weekly": "ਹਫ਼ਤਾਵਾਰੀ", "Monthly": "ਮਹੀਨਾਵਾਰ",
        "Yearly": "ਸਾਲਾਨਾ", "Apply": "ਲਾਗੂ ਕਰੋ", "Clear": "ਸਾਫ਼ ਕਰੋ", "Cancel": "ਰੱਦ ਕਰੋ",
        "Add transaction": "ਲੈਣ-ਦੇਣ ਜੋੜੋ", "Save transaction": "ਲੈਣ-ਦੇਣ ਸੰਭਾਲੋ", "Amount": "ਰਕਮ",
        "Category": "ਸ਼੍ਰੇਣੀ", "Description": "ਵੇਰਵਾ", "Date": "ਤਾਰੀਖ",
    },
    "sa": {
        "WORKSPACE": "कार्यक्षेत्रम्", "Overview": "सारांशः", "Transactions": "व्यवहाराः", "Notes": "टिप्पण्यः",
        "Calendar": "पञ्चाङ्गम्", "Cash calculator": "धनगणकम्", "PREFERENCES": "प्राथमिकताः", "Settings": "व्यवस्थाः", "About": "विषये", "About Cashbook": "लेखापुस्तकविषये",
        "Sign out": "निर्गच्छतु", "Profile": "परिचयः", "Language": "भाषा",
        "Choose the language used across your cashbook.": "भवतः लेखापुस्तके प्रयुक्तां भाषां चिनोतु।",
        "Display language": "प्रदर्शनभाषा", "Save language": "भाषां रक्षतु", "Cash in": "धनागमः",
        "Cash out": "धनव्ययः", "Daily": "प्रतिदिनम्", "Weekly": "प्रतिसप्ताहम्", "Monthly": "प्रतिमासम्",
        "Yearly": "प्रतिवर्षम्", "Apply": "प्रयुङ्क्ताम्", "Clear": "अपनयतु", "Cancel": "निरस्यतु",
        "Add transaction": "व्यवहारं योजयतु", "Save transaction": "व्यवहारं रक्षतु", "Amount": "राशिः",
        "Category": "वर्गः", "Description": "विवरणम्", "Date": "तिथिः",
    },
    "ta": {
        "WORKSPACE": "பணியிடம்", "Overview": "கண்ணோட்டம்", "Transactions": "பரிவர்த்தனைகள்", "Notes": "குறிப்புகள்",
        "Calendar": "நாள்காட்டி", "Cash calculator": "பணக் கணிப்பான்", "PREFERENCES": "விருப்பங்கள்", "Settings": "அமைப்புகள்", "About": "பற்றி", "About Cashbook": "பணப் பதிவேட்டைப் பற்றி",
        "Sign out": "வெளியேறு", "Profile": "சுயவிவரம்", "Language": "மொழி",
        "Choose the language used across your cashbook.": "உங்கள் பணப் பதிவேட்டில் பயன்படுத்தப்படும் மொழியைத் தேர்ந்தெடுக்கவும்.",
        "Display language": "காட்சி மொழி", "Save language": "மொழியைச் சேமி", "Cash in": "பணம் வரவு",
        "Cash out": "பணம் செலவு", "Daily": "தினசரி", "Weekly": "வாராந்திரம்", "Monthly": "மாதாந்திரம்",
        "Yearly": "ஆண்டுதோறும்", "Apply": "பயன்படுத்து", "Clear": "அழி", "Cancel": "ரத்துசெய்",
        "Add transaction": "பரிவர்த்தனையைச் சேர்", "Save transaction": "பரிவர்த்தனையைச் சேமி", "Amount": "தொகை",
        "Category": "வகை", "Description": "விவரம்", "Date": "தேதி",
    },
    "te": {
        "WORKSPACE": "పని ప్రదేశం", "Overview": "సారాంశం", "Transactions": "లావాదేవీలు", "Notes": "గమనికలు",
        "Calendar": "క్యాలెండర్", "Cash calculator": "నగదు కాలిక్యులేటర్", "PREFERENCES": "ప్రాధాన్యతలు", "Settings": "సెట్టింగ్‌లు", "About": "గురించి", "About Cashbook": "క్యాష్‌బుక్ గురించి",
        "Sign out": "సైన్ అవుట్", "Profile": "ప్రొఫైల్", "Language": "భాష",
        "Choose the language used across your cashbook.": "మీ క్యాష్‌బుక్‌లో ఉపయోగించే భాషను ఎంచుకోండి.",
        "Display language": "ప్రదర్శన భాష", "Save language": "భాషను సేవ్ చేయండి", "Cash in": "నగదు జమ",
        "Cash out": "నగదు ఖర్చు", "Daily": "రోజువారీ", "Weekly": "వారానికొకసారి", "Monthly": "నెలవారీ",
        "Yearly": "సంవత్సరానికి", "Apply": "వర్తింపజేయండి", "Clear": "తొలగించండి", "Cancel": "రద్దు చేయండి",
        "Add transaction": "లావాదేవీని జోడించండి", "Save transaction": "లావాదేవీని సేవ్ చేయండి", "Amount": "మొత్తం",
        "Category": "వర్గం", "Description": "వివరణ", "Date": "తేదీ",
    },
    "ur": {
        "WORKSPACE": "کام کی جگہ", "Overview": "جائزہ", "Transactions": "لین دین", "Notes": "نوٹس",
        "Calendar": "کیلنڈر", "Cash calculator": "نقد کیلکولیٹر", "PREFERENCES": "ترجیحات", "Settings": "ترتیبات", "About": "کے بارے میں", "About Cashbook": "کیش بک کے بارے میں",
        "Sign out": "سائن آؤٹ", "Profile": "پروفائل", "Language": "زبان",
        "Choose the language used across your cashbook.": "اپنی کیش بک میں استعمال ہونے والی زبان منتخب کریں۔",
        "Display language": "دکھانے کی زبان", "Save language": "زبان محفوظ کریں", "Cash in": "نقد آمد",
        "Cash out": "نقد خرچ", "Daily": "روزانہ", "Weekly": "ہفتہ وار", "Monthly": "ماہانہ",
        "Yearly": "سالانہ", "Apply": "لاگو کریں", "Clear": "صاف کریں", "Cancel": "منسوخ کریں",
        "Add transaction": "لین دین شامل کریں", "Save transaction": "لین دین محفوظ کریں", "Amount": "رقم",
        "Category": "زمرہ", "Description": "تفصیل", "Date": "تاریخ",
    },
}


def main():
    locale_root = Path(__file__).resolve().parents[1] / "locale"
    for code, translations in TRANSLATIONS.items():
        lines = [
            'msgid ""',
            'msgstr ""',
            '"Content-Type: text/plain; charset=UTF-8\\n"',
            f'"Language: {code}\\n"',
            '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
            "",
        ]
        for source, translated in translations.items():
            lines += [f"msgid {json.dumps(source, ensure_ascii=False)}", f"msgstr {json.dumps(translated, ensure_ascii=False)}", ""]
        output = locale_root / code / "LC_MESSAGES" / "django.po"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {output.relative_to(locale_root.parent)} ({len(translations)} entries)")


if __name__ == "__main__":
    main()
