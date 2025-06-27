from fastapi import FastAPI
import random
import asyncio
import httpx
from datetime import datetime

app = FastAPI()

def generate_sensor_data(abnormal=False):
    def normal_range(sensor):
        return {
            "soil_moisture": round(random.uniform(65.0, 80.0), 2),
            "temperature": round(random.uniform(15.0, 24.0), 2),
            "humidity": round(random.uniform(60.0, 80.0), 2)
        }[sensor]

    def abnormal_range(sensor):
        ranges = {
            "soil_moisture": [random.uniform(60.0, 64.9), random.uniform(80.1, 83.0)],
            "temperature": [random.uniform(13.0, 14.9), random.uniform(24.1, 26.0)],
            "humidity": [random.uniform(58.0, 59.9), random.uniform(80.1, 82.0)]
        }
        return round(random.choice(ranges[sensor]), 2)

    data = {
        "soil_moisture": normal_range("soil_moisture"),
        "temperature": normal_range("temperature"),
        "humidity": normal_range("humidity"),
    }

    if abnormal:
        affected = random.sample(["soil_moisture", "temperature", "humidity"], k=random.randint(1, 3))
        for sensor in affected:
            data[sensor] = abnormal_range(sensor)

    data["timestamp"] = datetime.now().isoformat()
    return data

@app.on_event("startup")
async def start_sending():
    async def sender_loop():
        abnormal = False
        counter = 0

        while True:
            if counter >= 6:
                abnormal = not abnormal
                counter = 0
                print(f"\n🔄 Mode switched to: {'ABNORMAL' if abnormal else 'NORMAL'}")

            data = generate_sensor_data(abnormal=abnormal)
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
