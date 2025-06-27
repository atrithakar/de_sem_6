from fastapi import FastAPI
import random
import asyncio
import httpx
from datetime import datetime

app = FastAPI()

def generate_sensor_data(mode='normal'):
    if mode == 'normal':
        soil_moisture = round(random.uniform(65.0, 80.0), 2)
        temperature = round(random.uniform(15.0, 24.0), 2)
        humidity = round(random.uniform(60.0, 80.0), 2)
    else:
        soil_moisture = round(random.choice([
            random.uniform(60.0, 64.9),
            random.uniform(80.1, 83.0)
        ]), 2)

        temperature = round(random.choice([
            random.uniform(13.0, 14.9),
            random.uniform(24.1, 26.0)
        ]), 2)

        humidity = round(random.choice([
            random.uniform(58.0, 59.9),
            random.uniform(80.1, 82.0)
        ]), 2)

    return {
        "timestamp": datetime.now().isoformat(),
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity
    }

@app.on_event("startup")
async def start_sending():
    async def sender_loop():
        mode = 'normal'
        counter = 0
        while True:
            if counter >= 6:
                mode = 'abnormal' if mode == 'normal' else 'normal'
                counter = 0
                print(f"\n🔄 Mode switched to: {mode.upper()}")

            data = generate_sensor_data(mode)
            print(f"📤 Sending: {data}")
            try:
                async with httpx.AsyncClient() as client:
                    await client.post("http://localhost:8001/receive", json=data)
            except Exception as e:
                print(f"❌ Error sending data: {e}")

            counter += 1
            await asyncio.sleep(10)

    asyncio.create_task(sender_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
