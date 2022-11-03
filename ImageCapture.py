from farmbot import Farmbot, FarmbotToken
from MoveHandler import TakePicturesHandler

if __name__ == '__main__':
    email = "dummy_value"
    password = "dummy_value"
    raw_token = FarmbotToken.download_token(email, password)

    handler = TakePicturesHandler()
    handler.x = 0
    handler.y = 0
    handler.z = 0
    fb = Farmbot(raw_token)
    fb.connect(handler)
