import truststore
truststore.inject_into_ssl()
import anthropic
client = anthropic.Anthropic()
try:
    r = client.messages.create(model="claude-haiku-5-5", max_tokens=50,
        messages=[{"role": "user", "content": "Bonjour"}])
    print(r.content[0].text)
except Exception as e:
    print("ERREUR:", repr(e), "| CAUSE:", repr(e.__cause__))
