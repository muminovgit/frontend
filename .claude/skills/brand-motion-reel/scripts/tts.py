# Microsoft Edge neural TTS through the agent proxy.  python3 tts.py "<text>" out.mp3 [rate] [pitch] [voice]
# Uzbek voices: uz-UZ-MadinaNeural (female), uz-UZ-SardorNeural (male).
# Energetic/cheerful female preset that the user approved: rate "+8%", pitch "+18Hz", text with "!" — then voice_fx.sh.
import sys, os, asyncio, certifi
certifi.where = lambda: '/root/.ccr/ca-bundle.crt'   # aiohttp ignores SSL_CERT_FILE; the proxy re-terminates TLS
import edge_tts
text, out = sys.argv[1], sys.argv[2]
rate = sys.argv[3] if len(sys.argv) > 3 else '+0%'
pitch = sys.argv[4] if len(sys.argv) > 4 else '+0Hz'
voice = sys.argv[5] if len(sys.argv) > 5 else 'uz-UZ-MadinaNeural'
asyncio.run(edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=os.environ.get('HTTPS_PROXY')).save(out))
