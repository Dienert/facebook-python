## Facebook Friends Crawler

### Configuration Steps
1. First thing to do is set email em password of the user in the file "capture/acess", each one in a line.
1. Install the python depencies.
1. Install mongodb and create a database called "facebook"

### Execution
1. Run the spider "facebook_spyder.py" in the "capture" folder with the following command line:

#### scrapy runspider facebook_spyder.py -L INFO

After the execution you can see the data in mongodb using RoboMongo, for example.

2. You can generate the proper json file used by grafico.html visualization running the following commando in the "capture" folder:

#### python export_json.py

3. You can persist the friends pictures running:

#### python get_images.py
