import requests
import openai
import os
import time
import json
import shutil
from flask import Flask, jsonify
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("API_KEY")
mesh_api_key = os.getenv("MESHY_API_KEY")  # You can add this if needed later

# Define allowed categories
envs = ['road', 'terrain', 'grass', 'snow']
static_obs = ['log', 'cactus', 'barricade']
dynamic_obs = ['car', 'jeep', 'zombie', 'train', 'tiger']

def understanding_concept(concept_info):
    """
    Uses OpenAI to extract environment, static obstacle, and dynamic obstacle keywords from concept text.
    """
    prompt = f"""
    Using the information below, classify and return three keywords:
    1) Environment type from {envs}
    2) Static obstacle type from {static_obs}
    3) Dynamic obstacle type from {dynamic_obs}

    Input:
    "{concept_info}"

    Strictly return as: "environment, staticObstacle, DynamicObstacle"
    If keywords are not found, randomly generate from the lists.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant for game asset generation. Extract relevant environment and obstacle keywords."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

def move_file(source_path, destination_path):
    """
    Copies a file from source to destination.
    """
    try:
        shutil.copy(source_path, destination_path)
        print(f"File copied from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"File not found: {source_path}")
    except PermissionError:
        print(f"Permission denied: {source_path}")
    except Exception as e:
        print(f"Error while copying file: {e}")

@app.route('/generate/<concept>', methods=['GET'])
def get_3d_models(concept):
    """
    Flask route to process concept, classify environment & obstacles,
    and copy the appropriate assets to Unity folders.
    """
    prompts = understanding_concept(concept)
    print("Prompts:", prompts)

    # Example relative paths (replace as per your actual project structure)
    texture_src = "./Assets/Textures/"
    static_obj_src = "./Assets/Prefabs/StaticObjs/"
    moving_obj_src = "./Assets/Prefabs/MovingObjs/"

    texture_dest = "./Assets/Resources/Materials/"
    static_obj_dest = "./Assets/Resources/StaticObjs/"
    moving_obj_dest = "./Assets/Resources/MovingObjs/"

    try:
        environment, static_obstacle, dynamic_obstacle = prompts.split(',')
        environment = environment.strip('" [')
        static_obstacle = static_obstacle.strip('" ]')
        dynamic_obstacle = dynamic_obstacle.strip('" ]')

        if environment not in envs or static_obstacle not in static_obs or dynamic_obstacle not in dynamic_obs:
            raise ValueError("Invalid keywords")

    except Exception as e:
        print("Parsing failed, using default:", e)
        environment, static_obstacle, dynamic_obstacle = "road", "barricade", "car"

    # Copy assets
    move_file(f"{texture_src}{environment}.mat", f"{texture_dest}roadMat.mat")
    move_file(f"{static_obj_src}{static_obstacle}.prefab", f"{static_obj_dest}staticObj.prefab")
    move_file(f"{moving_obj_src}{dynamic_obstacle}.prefab", f"{moving_obj_dest}movingObj.prefab")

    print("File operations completed.")
    time.sleep(1)

    return jsonify({"keywords": [environment, static_obstacle, dynamic_obstacle]})

if __name__ == '__main__':
    app.run(port=5000)
