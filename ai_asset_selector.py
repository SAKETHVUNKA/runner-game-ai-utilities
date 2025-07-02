import requests
import openai
import os
import time
import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from os import getenv
import shutil
import time

app = Flask(__name__)

load_dotenv()
openai.api_key = getenv("API_KEY")
meshApi = "msy_vagZukwm0TmAMBOk9I5gip0C4jNeJlOf7btz"
taskIds = []

envs = ['road', 'terrain','grass','snow']
statObs = ['log','cactus','barricade']
dynaObs = ['car','jeep','zombie','train','tiger']

def understanding_concept(concept_info):
  prompt = f"""
    Using the information provided below, please classify and get the two keywords. First being the type of environment or scene and second being the obstacle type (like wooden pieces, cars, etc). For the environment, please use one of the below: '{envs}' suitable to the provided information. 
    For the static Obstacle, please use one of the below: '{statObs}' suitable to the provided information. For the dynamic Obstacle, please use one of the below: '{dynaObs}' suitable to the provided information
    Provided information:
   "{concept_info}"
    Stricly keep the response in a list, it has to be in the following format:
    "environment, staticObstacle, DynamicObstacle"
    and never dont say "doesnt match" if the keywords are not found in the response, generate randomly from the given list.
    """

  response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[{
          "role":
          "system",
          "content":
          "You are an AI assistant capable of understanding the concept, context, and style for advertisement campaigns. Extract relevant information from the provided input."
      }, {
          "role": "user",
          "content": prompt
      }])
  return response.choices[0].message.content.strip()

def generate3D(prompts):

  headers = {"Authorization": f"Bearer {meshApi}"}
  for prompt in prompts:
    payload = {
        "object_prompt": f"{prompt}",
        "style_prompt":
        "High Quality cartoon model with no damage and should look new",
        "enable_pbr": True,
        "art_style": "realistic",
        "negative_prompt": "low quality, low resolution, low poly, ugly"
    }

    response = requests.post(
        "https://api.meshy.ai/v1/text-to-3d",
        headers=headers,
        json=payload,
    )
    taskIds.append(response.json())
  return taskIds


def extract3DModels(taskIds):
  headers = {"Authorization": f"Bearer {meshApi}"}
  models = []

  # while(1):
  #   for taskId in taskIds:
  #     response = requests.get(f"https://api.meshy.ai/v1/text-to-3d/{taskId['result']}",
  #                             headers=headers)
  #     print(response.json())
  #     time.sleep(10)
  #     imodel_url!
  while True:
    resp_flag = []
    for taskId in taskIds:
      response = requests.get(f"https://api.meshy.ai/v1/text-to-3d/{taskId['result']}",
                              headers=headers)
      if response.json()['status'].upper() == 'SUCCEEDED':
        resp_flag.append(True)
      else:
        resp_flag.append(False)
    time.sleep(10)
    if all(resp_flag):
      break
  for taskId in taskIds:
    response = requests.get(f"https://api.meshy.ai/v1/text-to-3d/{taskId['result']}",
                            headers=headers)
    models.append(response.json())
  return models


def getRequestStatus(models):
  for i in models:
    print(i['status'] , " ", i['model_url'])



def move_file(source_path, destination_path):

    try:

        shutil.copy(source_path, destination_path)
        print(f"File copy pasted successfully from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"The file at {source_path} was not found.")
    except PermissionError:
        print(f"Permission denied: unable to move the file at {source_path}")
    except Exception as e:
        print(f"An error occurred while moving the file: {e}")

@app.route('/generate/<concept>', methods=['GET'])
def get3DModels(concept):
  concept_info = "A game level where players navigate a post-apocalyptic city with ruined buildings and avoid zombie hordes."
  prompts = understanding_concept(concept)
  print("Prompt",prompts)
  texture_src = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\textures\\Road\\"
  static_obj_src = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\Perfabs\\staticObjs\\"
  moving_obj_src = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\Perfabs\\movingObjs\\"
  texture_dest = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\Resources\\Materials\\"
  static_obj_dest = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\Resources\\StaticObjs\\"
  moving_obj_dest = "D:\\Unity Learn\\Kodikon3.0\\Road-Runner-master\\Assets\\Resources\\MovingObjs\\"
  try:
      environment, staticObstacle, DynamicObstacle = prompts.split(',')
      environment = environment.lstrip('"[').rstrip('"')
      staticObstacle = staticObstacle.lstrip(' "').rstrip('"')
      DynamicObstacle = DynamicObstacle.lstrip(' "').rstrip('"]')
      print(environment)
      print(staticObstacle)
      print(DynamicObstacle)
      if environment not in envs or staticObstacle not in statObs or DynamicObstacle not in dynaObs:
          raise ValueError
  except Exception as e:
      print(e)
      environment, staticObstacle, DynamicObstacle = "road", "barricade", "car"

  move_file(texture_src+environment+".mat",texture_dest+"roadMat"+".mat")
  move_file(static_obj_src+staticObstacle+".prefab",static_obj_dest+"stone"+".prefab")
  move_file(moving_obj_src+DynamicObstacle+".prefab",moving_obj_dest+"car"+".prefab")
  # taskIds = generate3D(["Horror Environment", "zombie"])
  # print(taskIds)
##  models = extract3DModels(taskIds)
##  getRequestStatus(models)
  print("Im in flask func")

  time.sleep(5)
  
  return jsonify([f"{prompts}"])


if __name__ == '__main__':
   app.run(port=5000)