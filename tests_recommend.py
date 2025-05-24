import requests
import random
list_username:list = [
    {
        "username_or_email":"miguel_garcia87",
        "password":"M1gu3l#2025"
    },
    {
        "username_or_email":"juan_perez01",
        "password":"Ju4nP3r3z_01"
    }
]
posts = [
  {
    "content": "¡Qué día tan increíble en la playa! 🌊☀️",
    "media_urls": [
      "https://example.com/media/beach_photo.jpg",
      "https://example.com/media/beach_video.mp4"
    ],
  },
  {
    "content": "Probando una nueva receta de pasta 🍝 #CocinaConAmor",
    "media_urls": [
      "https://example.com/media/pasta_dish.jpg"
    ],
  },
  {
    "content": "Reflexionando sobre la vida mientras miro las estrellas ✨",
    "media_urls": [],
  },
  {
    "content": "Entrenamiento de hoy: 5K en el parque 🏃‍♂️💪",
    "media_urls": [
      "https://example.com/media/running_selfie.jpg",
      "https://example.com/media/park_view.png"
    ],
  }
]
list_token_access:list=[]

for user in list_username:
    response = requests.post(url="http://127.0.0.1:5000/api/auth/login",json=user)
    list_token_access.append(response.json()['token'])
    print(response.status_code)
    print(response.json())
for post in posts:
    numac:int = random.randint(0,1)
    response = requests.post(url="http://127.0.0.1:5000/api/posts",json=post,headers={
    "Authorization": f"Bearer {list_token_access[numac]}",
    "Content-Type": "application/json"  
    })

    print(response.status_code)
    print(response.json())

