from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import VitsTokenizer, VitsModel
import torch
import soundfile as sf
import io
from fastapi.responses import StreamingResponse

class VoiceOption(str, Enum):
    thai_male = "thai-male"
    thai_female = "thai-female"
    english_male = "english-male"
    english_female = "english-female"

class TTSRequest(BaseModel):
    text: str = Field(..., example="สวัสดีครับ")
    voice: VoiceOption = Field(..., description="เลือกเสียงที่ต้องการ")

app = FastAPI(
    title="Thai-English TTS API",
    description="""
API สำหรับแปลงข้อความเป็นเสียง (Text to Speech)

**Endpoint**: `POST /tts/`

### Voice options:
- `thai-male` : ภาษาไทย เสียงชาย
- `thai-female` : ภาษาไทย เสียงหญิง
- `english-male` : ภาษาอังกฤษ เสียงชาย
- `english-female` : ภาษาอังกฤษ เสียงหญิง (จำลอง)
""",
    version="1.0.0"
)

# โหลดโมเดล
male_model = VitsModel.from_pretrained("VIZINTZOR/MMS-TTS-THAI-MALEV2")
male_tokenizer = VitsTokenizer.from_pretrained("VIZINTZOR/MMS-TTS-THAI-MALEV2")

female_model = VitsModel.from_pretrained("VIZINTZOR/MMS-TTS-THAI-FEMALEV2")
female_tokenizer = VitsTokenizer.from_pretrained("VIZINTZOR/MMS-TTS-THAI-FEMALEV2")

eng_model = VitsModel.from_pretrained("facebook/mms-tts-eng")
eng_tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-eng")

def synthesize_speech(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        speech = model(**inputs).waveform
    sr = model.config.sampling_rate if hasattr(model.config, "sampling_rate") else 22050
    buffer = io.BytesIO()
    sf.write(buffer, speech.squeeze().numpy(), sr, format="wav")
    buffer.seek(0)
    return buffer

@app.post("/tts/", summary="แปลงข้อความเป็นเสียง")
async def tts_endpoint(request: TTSRequest):
    if request.voice == VoiceOption.thai_male:
        buffer = synthesize_speech(male_model, male_tokenizer, request.text)
    elif request.voice == VoiceOption.thai_female:
        buffer = synthesize_speech(female_model, female_tokenizer, request.text)
    elif request.voice == VoiceOption.english_male:
        buffer = synthesize_speech(eng_model, eng_tokenizer, request.text)
    elif request.voice == VoiceOption.english_female:
        eng_text = f"[SPEAKER:en_female]\n{request.text}"
        buffer = synthesize_speech(eng_model, eng_tokenizer, eng_text)
    else:
        raise HTTPException(status_code=400, detail="Invalid voice option")

    return StreamingResponse(buffer, media_type="audio/wav", headers={
        "Content-Disposition": f"attachment; filename={request.voice}_output.wav"
    })
