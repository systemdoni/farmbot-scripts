## Farmbot scripts
Python scripts to call the Farmbot API. Before running the scripts install the requirements that are in the `requirements.txt` file. The `downloader.py` requires the `requests` library, while `ImageCapture.py` requires `farmbot` library

**_Make sure to change the `email` and `password` variables inside the scripts to the correct values. Right now they have dummy values so the scripts won't work. Right now their values are:_**
```python
email = "dummy_value"
password = "dummy_value"
```

### Downloader
The functions here in general are self-descriptive and easy to understand.

The download checks and downloads all the images for **two weeks**, if they have not been already downloaded.
The save location is `img_dir = "/var/www/html/images/"`, which can be changes, but with this path,
it is supposed you have apache installed and the user has permission to create images directory and
save files inside. If you want to limit user to write only inside images without doing other modifications
with user permissions, you can also just create the images directory before running the script and make the user an owner
so it will be able to read and write.
To automate the script I used crontab. Run 
```bash 
$ crontab -e
``` 
with the user which is the owner of the images directory
and paste the following command at the bottom. (**_Make sure to change the path of the script location and the logs
As you can see right now it as my username on it since I had it saved in my home directory_**):

```
0 12 * * * python3 /home/doni/downloader.py > /home/doni/logs-downloader.txt 2>&1
```

This will run the script every day at 12 (server time).

There is also a batch delete function which deletes all images in the images data.
Before calling it you need to call the `get_images` function first, like this:
```
images_data = get_images(token)
batch_delete_photos(token, images_data)
```
get_images return images for a few days, so if you would like to delete all images, you would need to do it
by calling the batch delete in a loop until all of them are deleted.

### Image Capture & Move Handler

#### Image Capture
`ImageCapture.py` simply does the authentication and then initializes the `TakePictureHandler` which will be used by the farmbot library to make the backend calls.

#### Move Handler

`MoveHandler.py` contains the implementation of `TakePictureHandler`

TakePictureHandler is a customized version of the handler from farmbot's repo: https://github.com/FarmBot/farmbot-py

The functionality is described inside the script by the farmbot team, so I will only give some details about the newly added parameters

An explanation of the parameters used:
- `x,y,z` are the coordinates of the camera. Before taking the picture we position the camera at these coordinates.
- `w_icrement` and `h_increment` are the values with which the x and y coordinates are incremented everytime to move camera to take the next picture.
The problem here is that based on the web interface, I assumed that the values so the pictures won't overlap are 340x230, but in reality pictures overlap,
so there must be done some testing to see which movement is the best to not cause overlapping, and avoid the need to use
image stitching algorithms that deal with overlapping. I had troubles doing the stitching.
- `garden_w` and `garden_h` are the maximum values where the camera may go, the other corner of the garden.
- `mqtt_client`: mqtt_client object, saved to call disconnect on it.
- `photo_request_id`: keeps the id of the photo request action, needed to know when to run the logic related to taking pictures.
- `beginning`, `reverse_movement`, `y_changed`: parameters I used to move the camera around, scanning the entire garden going from right to left and left to right and so on.
Shouldn't be changed.
