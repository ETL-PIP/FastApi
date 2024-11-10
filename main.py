from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

# MongoDB URI and Database Configuration
MONGO_URI = "mongodb+srv://admin:samir5636@cluster0.ghz8l.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "sample_mflix"
COLLECTION_NAME = "combined_data_collection"

# Initialize FastAPI and MongoDB client
app = FastAPI()
client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client[DATABASE_NAME]

# Define allowed origins for CORS (you can add specific origins if needed)
origins = [
    "http://localhost",        # Allow localhost (useful for development)
    "http://localhost:3000",   # Example for frontend running on port 3000
    # Add other origins as needed
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows only the specified origins
    allow_credentials=True,
    allow_methods=["*"],               # Allows all HTTP methods
    allow_headers=["*"],               # Allows all headers
)

# Define Pydantic models for the data schema
class PlayerAppearance(BaseModel):
    appearance_id: str
    game_id: int
    player_id: int
    player_club_id: int
    player_current_club_id: int
    date: str
    player_name: str
    competition_id: str
    yellow_cards: int
    red_cards: int
    goals: int
    assists: int
    minutes_played: int

# Create a test endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Fetch all documents in the collection
@app.get("/appearances", response_model=List[PlayerAppearance])
async def get_all_appearances():
    appearances = []
    cursor = db[COLLECTION_NAME].find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        appearances.append(document)
    return appearances

# Fetch a single document by player_id
@app.get("/appearances/{player_id}", response_model=PlayerAppearance)
async def get_appearance_by_player_id(player_id: int):
    document = await db[COLLECTION_NAME].find_one({"player_id": player_id})
    if document:
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return document
    raise HTTPException(status_code=404, detail="Player not found")

# Close the MongoDB client when the app stops
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
